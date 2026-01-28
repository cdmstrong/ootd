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


def _get_missing_parts(provided_parts: List[str]) -> List[str]:
    """Get the list of clothing parts that are NOT provided."""
    all_parts = ["TOP", "PANTS", "SHOES", "BAG"]
    return [p for p in all_parts if p not in provided_parts]


def _format_part_list(parts: List[str]) -> str:
    """Format a list of parts into a readable string."""
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0].lower()
    if len(parts) == 2:
        return f"{parts[0].lower()} and {parts[1].lower()}"
    # 3 parts
    return f"{parts[0].lower()}, {parts[1].lower()} and {parts[2].lower()}"


def _build_replacement_prompt(parts: List[str]) -> str:
    """Build the main replacement prompt based on provided parts."""
    if not parts:
        # No accessories provided, just return the original image description
        return (
            "Use the person from the first image as-is. "
            "Keep all clothing items exactly as they appear in the original image. "
            "Style: {style_desc}. Properly aligned, natural pose, correct body proportions, "
            "realistic fabric folds, photorealistic style, soft lighting, plain background."
        )

    part_descriptions = []
    if "TOP" in parts:
        part_descriptions.append("wearing the {top_desc}")
    if "PANTS" in parts:
        part_descriptions.append("wearing the {pants_desc}")
    if "SHOES" in parts:
        part_descriptions.append("wearing the {shoes_desc}")
    if "BAG" in parts:
        part_descriptions.append("carrying the {bag_desc}")

    if len(part_descriptions) == 1:
        replacement_text = f"A person from the first image is {part_descriptions[0]} from the provided accessory image(s)."
    else:
        replacement_text = f"A person from the first image is {', '.join(part_descriptions[:-1])} and {part_descriptions[-1]} from the provided accessory images."

    return replacement_text


def build_prompt(req: CreateOutfitTaskRequest) -> str:
    """
    Build an English prompt based on which clothing parts are provided.
    The first image is always the person/base image, followed by accessory images.
    
    If keep_original=True, explicitly instruct to keep non-provided parts unchanged.
    If keep_original=False, only replace the provided accessories without constraints.
    """
    parts = sorted(_collect_parts(req))
    missing_parts = _get_missing_parts(parts)

    # Build the main replacement description
    replacement_text = _build_replacement_prompt(parts)

    # Build the constraint text based on keep_original flag
    if not parts:
        # No accessories provided
        constraint_text = ""
    elif req.keep_original and missing_parts:
        # Keep original parts unchanged
        missing_text = _format_part_list(missing_parts)
        constraint_text = f" Keep all other clothing items ({missing_text}) exactly as they appear in the first image."
    else:
        # No constraint on other parts
        constraint_text = ""

    style_desc = ", ".join(req.style_tags) if req.style_tags else "modern, fashionable"

    # Fallback descriptions if user does not provide ones
    top_desc = req.top_desc or "a stylish top"
    pants_desc = req.pants_desc or "stylish pants"
    shoes_desc = req.shoes_desc or "stylish shoes"
    bag_desc = req.bag_desc or "a stylish bag"

    # Combine all parts
    prompt = (
        f"{replacement_text}{constraint_text} "
        f"Style: {style_desc}. Properly aligned, natural pose, correct body proportions, "
        f"realistic fabric folds, photorealistic style, soft lighting, plain background."
    )

    # Format with descriptions
    prompt = prompt.format(
        top_desc=top_desc,
        pants_desc=pants_desc,
        shoes_desc=shoes_desc,
        bag_desc=bag_desc,
        style_desc=style_desc,
    )

    return prompt


