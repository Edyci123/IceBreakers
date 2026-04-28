"""
Pydantic schemas for profile request/response payloads.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ProfileUpdateRequest(BaseModel):
    """Fields the user can set via PUT /api/profile."""

    first_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="User's first name",
    )
    middle_name: str | None = Field(
        default=None,
        max_length=100,
        description="User's middle name (optional)",
    )
    last_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="User's last name",
    )
    bio: str | None = Field(
        default=None,
        min_length=1,
        max_length=1000,
        description="Short biography / description",
    )
    interests: list[str] | None = Field(
        default=None,
        max_length=20,
        description="List of interest tags (max 20)",
    )
    avatar_url: str | None = Field(
        default=None,
        max_length=500,
        description="URL to profile picture",
    )
    location: str | None = Field(
        default=None,
        max_length=255,
        description="City / country",
    )

    @field_validator("interests")
    @classmethod
    def validate_interest_tags(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        for tag in v:
            stripped = tag.strip()
            if not stripped:
                raise ValueError("Interest tags must not be empty strings.")
            if len(stripped) > 50:
                raise ValueError(
                    f"Each interest tag must be at most 50 characters (got {len(stripped)})."
                )
        # Return stripped tags
        return [tag.strip() for tag in v]


class ProfileResponse(BaseModel):
    """Returned by GET and PUT /api/profile."""

    id: uuid.UUID
    user_id: uuid.UUID
    first_name: str | None
    middle_name: str | None
    last_name: str | None
    bio: str | None
    interests: list[str] | None
    avatar_url: str | None
    location: str | None
    is_profile_complete: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
