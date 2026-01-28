"""Image processing utilities - background removal handling."""

from __future__ import annotations

import os
from typing import List

from .client import InferenceClient
from .models import CreateOutfitTaskRequest


async def process_images_for_inference(
    req: CreateOutfitTaskRequest,
    task_id: str,
    inference_client: InferenceClient,
) -> List[str]:
    """
    Process images for inference: remove background if needed via inference service.

    Args:
        req: The outfit task request
        task_id: Task ID for generating output paths
        inference_client: Client for calling inference service

    Returns:
        List of processed image paths in order: [person_image, accessory1, accessory2, accessory3]
    """
    processed_paths: List[str] = []
    output_dir = os.path.join("outputs", "bg_removed", task_id)
    os.makedirs(output_dir, exist_ok=True)

    # Process person image
    if req.person_bg_removed:
        processed_paths.append(req.person_image_path)
    else:
        output_path = os.path.join(output_dir, "person.png")
        processed_path = await inference_client.remove_background(
            image_path=req.person_image_path,
            output_path=output_path,
        )
        processed_paths.append(processed_path)

    # Process accessory images
    accessories = [
        (req.top_image_path, req.top_bg_removed, "top"),
        (req.pants_image_path, req.pants_bg_removed, "pants"),
        (req.shoes_image_path, req.shoes_bg_removed, "shoes"),
        (req.bag_image_path, req.bag_bg_removed, "bag"),
    ]

    accessory_count = 0
    for image_path, bg_removed, name in accessories:
        if image_path and accessory_count < 3:  # At most 3 accessories
            if bg_removed:
                processed_paths.append(image_path)
            else:
                output_path = os.path.join(output_dir, f"{name}.png")
                processed_path = await inference_client.remove_background(
                    image_path=image_path,
                    output_path=output_path,
                )
                processed_paths.append(processed_path)
            accessory_count += 1

    return processed_paths

