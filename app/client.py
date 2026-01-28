"""HTTP client for calling inference service."""

from __future__ import annotations

import base64
import os
from io import BytesIO
from typing import List

import httpx
from PIL import Image

from .models import CreateOutfitTaskRequest


class InferenceClient:
    """Client for calling the inference service."""

    def __init__(self, base_url: str | None = None):
        """
        Initialize the inference client.

        Args:
            base_url: Base URL of the inference service. If None, reads from INFERENCE_SERVICE_URL env var.
        """
        self.base_url = base_url or os.getenv("INFERENCE_SERVICE_URL", "http://localhost:8001")

    async def infer(
        self,
        prompt: str,
        image_paths: List[str],
        task_id: str,
        height: int = 1024,
        width: int = 1024,
        guidance_scale: float = 1.0,
        num_inference_steps: int = 10,
    ) -> str:
        """
        Call the inference service to generate an image.

        Args:
            prompt: Text prompt for generation
            image_paths: List of image paths (first is person/base, rest are accessories)
            task_id: Task ID for generating output filename
            height: Output image height
            width: Output image width
            guidance_scale: Guidance scale
            num_inference_steps: Number of inference steps

        Returns:
            Path to the generated image.

        Raises:
            httpx.HTTPError: If the inference service call fails.
        """
        # Prepare local output path (API layer handles saving)
        os.makedirs("outputs", exist_ok=True)
        output_path = os.path.join("outputs", f"{task_id}.png")

        # Prepare request
        request_data = {
            "prompt": prompt,
            "image_paths": image_paths,
            "height": height,
            "width": width,
            "guidance_scale": guidance_scale,
            "num_inference_steps": num_inference_steps,
        }

        # Call inference service
        async with httpx.AsyncClient(timeout=300.0) as client:  # 5 minute timeout for inference
            response = await client.post(f"{self.base_url}/infer", json=request_data)
            response.raise_for_status()
            result = response.json()

            if not result.get("success"):
                error_msg = result.get("error_message", "Unknown error")
                raise RuntimeError(f"Inference service error: {error_msg}")

            image_base64 = result.get("image_base64")
            if not image_base64:
                raise RuntimeError("Inference service did not return image_base64")

            # Decode base64 and save image locally
            image_bytes = base64.b64decode(image_base64)
            buffer = BytesIO(image_bytes)
            image = Image.open(buffer).convert("RGB")
            image.save(output_path, format="PNG")

            return output_path

    async def remove_background(
        self,
        image_path: str,
        output_path: str | None = None,
    ) -> str:
        """
        Call the inference service to remove background from an image.

        Args:
            image_path: Path to image (local or URL)
            output_path: Optional output path. If None, the service will generate one.

        Returns:
            Path to the image with background removed.

        Raises:
            httpx.HTTPError: If the background removal service call fails.
        """
        # Prepare request
        request_data = {
            "image_path": image_path,
            "output_path": output_path,
        }

        # Call background removal service
        async with httpx.AsyncClient(timeout=60.0) as client:  # 1 minute timeout for bg removal
            response = await client.post(f"{self.base_url}/remove_background", json=request_data)
            response.raise_for_status()
            result = response.json()

            if not result.get("success"):
                error_msg = result.get("error_message", "Unknown error")
                raise RuntimeError(f"Background removal service error: {error_msg}")

            return result.get("output_path") or output_path or image_path

    def collect_image_paths(self, req: CreateOutfitTaskRequest) -> List[str]:
        """
        Collect image paths from the request in the correct order.

        Args:
            req: The outfit task request

        Returns:
            List of image paths: [person_image, accessory1, accessory2, accessory3]
        """
        paths: List[str] = []

        # First: person image (required)
        paths.append(req.person_image_path)

        # Then: collect accessories (at most 3)
        accessory_paths: List[str] = []
        if req.top_image_path:
            accessory_paths.append(req.top_image_path)
        if req.pants_image_path:
            accessory_paths.append(req.pants_image_path)
        if req.shoes_image_path:
            accessory_paths.append(req.shoes_image_path)
        if req.bag_image_path:
            accessory_paths.append(req.bag_image_path)

        # Respect the "at most 3 accessories" rule
        accessory_paths = accessory_paths[:3]
        paths.extend(accessory_paths)

        return paths

