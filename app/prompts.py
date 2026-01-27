from __future__ import annotations

from typing import Dict, List

from .models import CreateOutfitTaskRequest


def _collect_parts(req: CreateOutfitTaskRequest) -> List[str]:
    parts: List[str] = []
    if req.top_image_path:
        parts.append("TOP")
    if req.pants_image_path:
        parts.append("PANTS")
    if req.shoes_image_path:
        parts.append("SHOES")
    if req.bag_image_path:
        parts.append("BAG")
    return parts


BASE_TEMPLATES: Dict[str, str] = {
    "TOP": (
        "Use the provided top image as the main clothing item. "
        "Create a complete outfit that matches this top, including pants, shoes and a bag. "
        "The top is {top_desc}. Style: {style_desc}. "
        "Generate a realistic full-body fashion photo, studio lighting, plain background."
    ),
    "PANTS": (
        "Use the provided pants image as the main clothing item. "
        "Create a complete outfit that matches these pants, including top, shoes and a bag. "
        "The pants are {pants_desc}. Style: {style_desc}. "
        "Generate a realistic full-body fashion photo, studio lighting, plain background."
    ),
    "SHOES": (
        "Use the provided shoes image as the main item. "
        "Create a complete outfit that matches these shoes, including top, pants and a bag. "
        "The shoes are {shoes_desc}. Style: {style_desc}. "
        "Generate a realistic full-body fashion photo, studio lighting, plain background."
    ),
    "BAG": (
        "Use the provided bag image as the main item. "
        "Create a complete outfit that matches this bag, including top, pants and shoes. "
        "The bag is {bag_desc}. Style: {style_desc}. "
        "Generate a realistic full-body fashion photo, studio lighting, plain background."
    ),
    "TOP+PANTS": (
        "Use the provided top and pants images as fixed clothing items. "
        "Generate matching shoes and a bag that complete the outfit. "
        "The top is {top_desc}. The pants are {pants_desc}. Style: {style_desc}. "
        "Generate a realistic full-body fashion photo, studio lighting, plain background."
    ),
    "TOP+SHOES": (
        "Use the provided top and shoes images as fixed clothing items. "
        "Generate matching pants and a bag that complete the outfit. "
        "The top is {top_desc}. The shoes are {shoes_desc}. Style: {style_desc}. "
        "Generate a realistic full-body fashion photo, studio lighting, plain background."
    ),
    "TOP+BAG": (
        "Use the provided top and bag images as fixed clothing items. "
        "Generate matching pants and shoes that complete the outfit. "
        "The top is {top_desc}. The bag is {bag_desc}. Style: {style_desc}. "
        "Generate a realistic full-body fashion photo, studio lighting, plain background."
    ),
    "PANTS+SHOES": (
        "Use the provided pants and shoes images as fixed clothing items. "
        "Generate a matching top and bag that complete the outfit. "
        "The pants are {pants_desc}. The shoes are {shoes_desc}. Style: {style_desc}. "
        "Generate a realistic full-body fashion photo, studio lighting, plain background."
    ),
    "PANTS+BAG": (
        "Use the provided pants and bag images as fixed clothing items. "
        "Generate a matching top and shoes that complete the outfit. "
        "The pants are {pants_desc}. The bag is {bag_desc}. Style: {style_desc}. "
        "Generate a realistic full-body fashion photo, studio lighting, plain background."
    ),
    "SHOES+BAG": (
        "Use the provided shoes and bag images as fixed items. "
        "Generate a matching top and pants that complete the outfit. "
        "The shoes are {shoes_desc}. The bag is {bag_desc}. Style: {style_desc}. "
        "Generate a realistic full-body fashion photo, studio lighting, plain background."
    ),
}


def build_prompt(req: CreateOutfitTaskRequest) -> str:
    """
    Build an English prompt based on which clothing parts are provided.
    """
    parts = sorted(_collect_parts(req))
    combo_key = "+".join(parts)

    template = BASE_TEMPLATES.get(
        combo_key,
        (
            "Create a complete outfit based on the provided reference clothing images. "
            "Style: {style_desc}. Generate a realistic full-body fashion photo, "
            "studio lighting, plain background."
        ),
    )

    style_desc = ", ".join(req.style_tags) if req.style_tags else "modern, fashionable"

    # Fallback descriptions if user does not provide ones
    top_desc = req.top_desc or "a stylish top"
    pants_desc = req.pants_desc or "stylish pants"
    shoes_desc = req.shoes_desc or "stylish shoes"
    bag_desc = req.bag_desc or "a stylish bag"

    prompt = template.format(
        top_desc=top_desc,
        pants_desc=pants_desc,
        shoes_desc=shoes_desc,
        bag_desc=bag_desc,
        style_desc=style_desc,
    )
    return prompt


