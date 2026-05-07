"""
Meeting repository — data-access layer for the Meeting model.
"""

import uuid
from datetime import datetime

from sqlalchemy import and_, or_, select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from icebreakers.meetings.domain.enums import MeetingSource, ProposalStatus
from icebreakers.meetings.domain.models import Meeting


class MeetingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, meeting_id: uuid.UUID) -> Meeting | None:
        result = await self._db.execute(
            select(Meeting)
            .options(selectinload(Meeting.proposer), selectinload(Meeting.receiver))
            .where(Meeting.id == meeting_id)
        )
        return result.scalar_one_or_none()

    async def create(self, meeting: Meeting) -> Meeting:
        self._db.add(meeting)
        await self._db.flush()
        await self._db.refresh(meeting)
        # Eagerly load relationships for response serialization
        result = await self._db.execute(
            select(Meeting)
            .options(selectinload(Meeting.proposer), selectinload(Meeting.receiver))
            .where(Meeting.id == meeting.id)
        )
        return result.scalar_one()

    async def update(self, meeting: Meeting) -> Meeting:
        merged = await self._db.merge(meeting)
        await self._db.flush()
        # Re-fetch with eager-loaded relationships
        result = await self._db.execute(
            select(Meeting)
            .options(selectinload(Meeting.proposer), selectinload(Meeting.receiver))
            .where(Meeting.id == merged.id)
        )
        return result.scalar_one()

    async def delete(self, meeting: Meeting) -> None:
        await self._db.delete(meeting)
        await self._db.flush()

    async def has_pending_between(
        self, user_a: uuid.UUID, user_b: uuid.UUID
    ) -> bool:
        """Check if there's already a pending meeting between two users (either direction)."""
        result = await self._db.execute(
            select(Meeting.id).where(
                or_(
                    and_(
                        Meeting.proposer_id == user_a,
                        Meeting.receiver_id == user_b,
                    ),
                    and_(
                        Meeting.proposer_id == user_b,
                        Meeting.receiver_id == user_a,
                    ),
                ),
                # At least one side is still pending
                or_(
                    Meeting.proposer_status == ProposalStatus.PENDING,
                    Meeting.receiver_status == ProposalStatus.PENDING,
                ),
            )
        )
        return result.scalar_one_or_none() is not None

    async def list_for_user(
        self,
        user_id: uuid.UUID,
        status_filter: ProposalStatus | None = None,
        role_filter: str | None = None,
    ) -> list[Meeting]:
        """
        List meetings involving the user.

        status_filter: filter by the *user's own* status in the meeting.
        role_filter: 'proposer' or 'receiver' to restrict which side.
        """
        conditions = []

        if role_filter == "proposer":
            conditions.append(Meeting.proposer_id == user_id)
            if status_filter is not None:
                conditions.append(Meeting.proposer_status == status_filter)
        elif role_filter == "receiver":
            conditions.append(Meeting.receiver_id == user_id)
            if status_filter is not None:
                conditions.append(Meeting.receiver_status == status_filter)
        else:
            # No role filter — return all meetings involving the user
            user_involved = or_(
                Meeting.proposer_id == user_id,
                Meeting.receiver_id == user_id,
            )
            if status_filter is not None:
                # Filter where the *user's own* status matches
                user_involved = or_(
                    and_(
                        Meeting.proposer_id == user_id,
                        Meeting.proposer_status == status_filter,
                    ),
                    and_(
                        Meeting.receiver_id == user_id,
                        Meeting.receiver_status == status_filter,
                    ),
                )
            conditions.append(user_involved)

        stmt = (
            select(Meeting)
            .options(selectinload(Meeting.proposer), selectinload(Meeting.receiver))
            .where(*conditions)
            .order_by(Meeting.created_at.desc())
        )
        result = await self._db.execute(stmt)
        return list(result.scalars().all())

    async def cleanup_expired_engine_meetings(self, now: datetime) -> int:
        """
        Delete engine-created meetings past their proposed_time
        where fewer than 2 participants accepted.
        Returns the number of deleted meetings.
        """
        stmt = (
            delete(Meeting)
            .where(
                Meeting.source == MeetingSource.ENGINE,
                Meeting.proposed_time.isnot(None),
                Meeting.proposed_time < now,
                # Not both accepted
                ~and_(
                    Meeting.proposer_status == ProposalStatus.ACCEPTED,
                    Meeting.receiver_status == ProposalStatus.ACCEPTED,
                ),
            )
            .returning(Meeting.id)
        )
        result = await self._db.execute(stmt)
        deleted_ids = result.scalars().all()
        await self._db.flush()
        return len(deleted_ids)
