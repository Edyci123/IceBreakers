"""
SQLAlchemy ORM model for the Meeting entity.

For user-created meetings (source=user):
    proposer_id  = the user who created the meeting (auto-accepted)
    receiver_id  = the invited user (starts as pending)

For engine-created meetings (source=engine):
    proposer_id  = matched participant A (starts as pending)
    receiver_id  = matched participant B (starts as pending)
    Neither is truly a "proposer" — both are matched candidates.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from icebreakers.meetings.domain.enums import MeetingSource, MeetingType, ProposalStatus
from icebreakers.shared.database import Base


class Meeting(Base):
    __tablename__ = "meetings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    proposer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    receiver_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    proposer_status: Mapped[ProposalStatus] = mapped_column(
        Enum(ProposalStatus, name="proposal_status", create_constraint=True),
        default=ProposalStatus.PENDING,
        nullable=False,
    )
    receiver_status: Mapped[ProposalStatus] = mapped_column(
        Enum(ProposalStatus, name="proposal_status", create_constraint=True),
        default=ProposalStatus.PENDING,
        nullable=False,
    )
    source: Mapped[MeetingSource] = mapped_column(
        Enum(MeetingSource, name="meeting_source", create_constraint=True),
        nullable=False,
    )
    meeting_type: Mapped[MeetingType] = mapped_column(
        Enum(MeetingType, name="meeting_type", create_constraint=True),
        default=MeetingType.COFFEEBREAK,
        nullable=False,
    )
    proposed_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    duration_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    proposer = relationship(
        "User", foreign_keys=[proposer_id], overlaps="proposed_meetings"
    )
    receiver = relationship(
        "User", foreign_keys=[receiver_id], overlaps="received_meetings"
    )

    def __repr__(self) -> str:
        return (
            f"<Meeting {self.id} "
            f"proposer={self.proposer_id} ({self.proposer_status.value}) "
            f"receiver={self.receiver_id} ({self.receiver_status.value})>"
        )
