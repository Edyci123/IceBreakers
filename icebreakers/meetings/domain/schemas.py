"""
Pydantic schemas for meeting request/response payloads.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from icebreakers.meetings.domain.enums import MeetingSource, MeetingType, ProposalStatus


class MeetingCreateRequest(BaseModel):
    """Fields for creating a new meeting proposal."""

    receiver_id: uuid.UUID = Field(
        description="UUID of the user to invite",
    )
    meeting_type: MeetingType = Field(
        default=MeetingType.COFFEEBREAK,
        description="Type of meeting",
    )
    proposed_time: datetime | None = Field(
        default=None,
        description="Suggested meeting datetime (ISO 8601)",
    )
    duration_minutes: int | None = Field(
        default=None,
        ge=5,
        le=480,
        description="Duration in minutes (5–480)",
    )
    location: str | None = Field(
        default=None,
        max_length=255,
        description="Meeting location",
    )
    message: str | None = Field(
        default=None,
        max_length=500,
        description="Icebreaker topic or message",
    )

    @model_validator(mode="after")
    def validate_coffeebreak_duration(self) -> "MeetingCreateRequest":
        if (
            self.meeting_type == MeetingType.COFFEEBREAK
            and self.duration_minutes is not None
            and self.duration_minutes > 30
        ):
            raise ValueError(
                "Coffeebreak meetings cannot exceed 30 minutes. "
                "Use meeting_type 'other' for longer meetings."
            )
        return self


class MeetingResponse(BaseModel):
    """Returned by all meeting endpoints."""

    id: uuid.UUID
    proposer_id: uuid.UUID
    receiver_id: uuid.UUID
    proposer_status: ProposalStatus
    receiver_status: ProposalStatus
    source: MeetingSource
    meeting_type: MeetingType
    proposed_time: datetime | None
    duration_minutes: int | None
    location: str | None
    message: str | None
    proposer_email: str
    receiver_email: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
