from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field, root_validator


PartType = Literal["TOP", "PANTS", "SHOES", "BAG"]

TaskStatus = Literal["PENDING", "RUNNING", "SUCCEEDED", "FAILED"]


class CreateOutfitTaskRequest(BaseModel):
    """
    Request body for creating an outfit generation task.

    Each image field is expected to be a local path or URL that
    the backend can read. At most two image fields may be non-empty.
    """

    top_image_path: Optional[str] = Field(default=None)
    pants_image_path: Optional[str] = Field(default=None)
    shoes_image_path: Optional[str] = Field(default=None)
    bag_image_path: Optional[str] = Field(default=None)

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

    @root_validator
    def validate_image_count(cls, values: Dict) -> Dict:
        """Ensure there is at least one and at most two images."""
        image_fields = [
            values.get("top_image_path"),
            values.get("pants_image_path"),
            values.get("shoes_image_path"),
            values.get("bag_image_path"),
        ]
        non_empty = [p for p in image_fields if p]
        if len(non_empty) == 0:
            raise ValueError("At least one clothing image must be provided.")
        if len(non_empty) > 2:
            raise ValueError("At most two clothing images can be provided per task.")
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


