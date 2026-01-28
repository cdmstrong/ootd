from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, root_validator


PartType = Literal["TOP", "PANTS", "SHOES", "BAG"]

TaskStatus = Literal["PENDING", "RUNNING", "SUCCEEDED", "FAILED"]


class CreateOutfitTaskRequest(BaseModel):
    """
    Request body for creating an outfit generation task.

    person_image_path is required (the base person/model image).
    Each accessory image field is expected to be a local path or URL that
    the backend can read. At most three accessory image fields may be non-empty.
    """

    person_image_path: str = Field(..., description="Required: Base person/model image (local path or URL)")
    person_bg_removed: bool = Field(
        default=False, description="Whether the person image already has background removed"
    )
    top_image_path: Optional[str] = Field(default=None, description="Top/clothing image (local path or URL)")
    top_bg_removed: bool = Field(default=False, description="Whether the top image already has background removed")
    pants_image_path: Optional[str] = Field(default=None, description="Pants image (local path or URL)")
    pants_bg_removed: bool = Field(
        default=False, description="Whether the pants image already has background removed"
    )
    shoes_image_path: Optional[str] = Field(default=None, description="Shoes image (local path or URL)")
    shoes_bg_removed: bool = Field(
        default=False, description="Whether the shoes image already has background removed"
    )
    bag_image_path: Optional[str] = Field(default=None, description="Bag image (local path or URL)")
    bag_bg_removed: bool = Field(default=False, description="Whether the bag image already has background removed")

    top_desc: Optional[str] = Field(
        default=None, description="Optional textual description of the top (e.g. white oversized t-shirt)."
    )
    pants_desc: Optional[str] = Field(
        default=None, description="Optional textual description of the pants (e.g. blue jeans)."
    )
    shoes_desc: Optional[str] = Field(
        default=None, description="Optional textual description of the shoes (e.g. white sneakers)."
    )
    bag_desc: Optional[str] = Field(
        default=None, description="Optional textual description of the bag (e.g. black leather handbag)."
    )

    style_tags: Optional[List[str]] = Field(
        default=None,
        description="Optional style or scenario tags, e.g. ['casual', 'office']",
    )

    keep_original: bool = Field(
        default=False,
        description="If True, keep non-provided clothing parts unchanged from the original image. "
        "If False, only replace the provided accessories without constraints on other parts.",
    )

    @root_validator(skip_on_failure=True)
    def validate_image_count(cls, values: Dict) -> Dict:
        """Ensure person_image_path is provided and at most three accessory images."""
        if not values.get("person_image_path"):
            raise ValueError("person_image_path is required.")
        accessory_fields = [
            values.get("top_image_path"),
            values.get("pants_image_path"),
            values.get("shoes_image_path"),
            values.get("bag_image_path"),
        ]
        non_empty = [p for p in accessory_fields if p]
        if len(non_empty) > 3:
            raise ValueError("At most three accessory images can be provided per task.")
        return values


class TaskInfo(BaseModel):
    task_id: str
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    input: CreateOutfitTaskRequest
    result: Optional[Dict] = None
    error_message: Optional[str] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    status: TaskStatus
    result: Optional[Dict] = None
    error_message: Optional[str] = None


