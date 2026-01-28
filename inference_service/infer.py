"""Pure inference logic - model loading and inference."""

from __future__ import annotations

import os
from io import BytesIO
from typing import List
from urllib.parse import urlparse

import requests
import torch
import sys
from pathlib import Path

# Add diffusers to path
sys.path.insert(0, str(Path(__file__).parent / "diffusers" / "src"))

from diffusers import Flux2KleinPipeline
from PIL import Image

_PIPELINE = None


def _get_device() -> str:
    """Get the device to run inference on."""
    return "cuda" if torch.cuda.is_available() else "cpu"


def _load_pipeline() -> Flux2KleinPipeline:
    """Load the Flux2KleinPipeline model (lazy loading, singleton)."""
    global _PIPELINE
    if _PIPELINE is None:
        device = _get_device()
        dtype = torch.bfloat16 if device == "cuda" else torch.float16
        # Model path relative to inference_service directory
        model_path = Path(__file__).parent / "flux2-klein" / "FLUX.2-klein-4B"
        _PIPELINE = Flux2KleinPipeline.from_pretrained(
            str(model_path),
            torch_dtype=dtype,
        )
        _PIPELINE.to(device)
    return _PIPELINE


def _load_image(path_or_url: str) -> Image.Image:
    """
    Load an image from either a local path or a URL.
    """
    parsed = urlparse(path_or_url)
    if parsed.scheme in ("http", "https"):
        # Download from URL
        response = requests.get(path_or_url, timeout=30)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content)).convert("RGB")
    else:
        # Local file path
        img = Image.open(path_or_url).convert("RGB")
    return img


def run_inference(
    prompt: str,
    image_paths: List[str],
    height: int = 1024,
    width: int = 1024,
    guidance_scale: float = 1.0,
    num_inference_steps: int = 10,
    output_path: str | None = None,
) -> str:
    """
    Run inference with the given prompt and images.

    Args:
        prompt: Text prompt for generation
        image_paths: List of image paths (first is person/base, rest are accessories)
        height: Output image height
        width: Output image width
        guidance_scale: Guidance scale
        num_inference_steps: Number of inference steps
        output_path: Optional output path. If None, generates a temporary path.

    Returns:
        Path to the generated image.
    """
    pipe = _load_pipeline()

    # Load all images
    images: List[Image.Image] = []
    for path in image_paths:
        img = _load_image(path)
        images.append(img)

    # Run inference
    result = pipe(
        prompt=prompt,
        image=images,
        height=height,
        width=width,
        guidance_scale=guidance_scale,
        num_inference_steps=num_inference_steps,
    ).images[0]

    # Save result
    if output_path is None:
        os.makedirs("outputs", exist_ok=True)
        import uuid

        output_path = os.path.join("outputs", f"{uuid.uuid4().hex}.png")
    else:
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)

    result.save(output_path)
    return output_path

