from __future__ import annotations

import os
from typing import List

from PIL import Image
import torch
from diffusers import Flux2KleinPipeline

from .models import CreateOutfitTaskRequest


_PIPELINE = None


def _get_device() -> str:
    return "cuda" if torch.cuda.is_available() else "cpu"


def _load_pipeline() -> Flux2KleinPipeline:
    global _PIPELINE
    if _PIPELINE is None:
        device = _get_device()
        dtype = torch.bfloat16 if device == "cuda" else torch.float16
        _PIPELINE = Flux2KleinPipeline.from_pretrained(
            "./flux2-klein/FLUX.2-klein-4B",
            torch_dtype=dtype,
        )
        _PIPELINE.to(device)
    return _PIPELINE


def _collect_images(req: CreateOutfitTaskRequest) -> List[Image.Image]:
    paths: List[str] = []
    if req.top_image_path:
        paths.append(req.top_image_path)
    if req.pants_image_path:
        paths.append(req.pants_image_path)
    if req.shoes_image_path:
        paths.append(req.shoes_image_path)
    if req.bag_image_path:
        paths.append(req.bag_image_path)
    # Respect the "at most 2 accessories" rule
    paths = paths[:2]

    images: List[Image.Image] = []
    for p in paths:
        img = Image.open(p).convert("RGB")
        images.append(img)
    return images


def generate_outfit_image(task_id: str, prompt: str, req: CreateOutfitTaskRequest) -> str:
    """
    Run the Flux2KleinPipeline with the given prompt and up to 2 conditioning images.

    Returns the output image path.
    """
    pipe = _load_pipeline()
    images = _collect_images(req)

    result = pipe(
        prompt=prompt,
        image=images,
        height=1024,
        width=1024,
        guidance_scale=1.0,
        num_inference_steps=10,
    ).images[0]

    os.makedirs("outputs", exist_ok=True)
    out_path = os.path.join("outputs", f"{task_id}.png")
    result.save(out_path)
    return out_path


