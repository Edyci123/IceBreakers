"""
Meeting service — business logic for meeting proposals.
"""

import logging
import uuid
from datetime import datetime, timedelta, timezone

from icebreakers.auth.infrastructure.repository import UserRepository
from icebreakers.meetings.domain.enums import MeetingSource, MeetingType, ProposalStatus
from icebreakers.meetings.domain.models import Meeting
from icebreakers.meetings.domain.schemas import MeetingCreateRequest
from icebreakers.meetings.infrastructure.repository import MeetingRepository

logger = logging.getLogger("icebreakers")

_STATUS_CHANGE_WINDOW = timedelta(hours=1)


class MeetingService:
    def __init__(self, repo: MeetingRepository, user_repo: UserRepository) -> None:
        self._repo = repo
        self._user_repo = user_repo

    async def create_proposal(
        self, proposer_id: uuid.UUID, data: MeetingCreateRequest
    ) -> Meeting:
        """
        Create a new meeting proposal.
        For user-created meetings, the proposer is auto-accepted.
        """
        if proposer_id == data.receiver_id:
            raise ValueError("You cannot create a meeting with yourself.")

        receiver = await self._user_repo.get_by_id(data.receiver_id)
        if receiver is None:
            raise LookupError("The specified receiver does not exist.")

        if await self._repo.has_pending_between(proposer_id, data.receiver_id):
            raise PermissionError(
                "There is already a pending meeting between you and this user."
            )

        meeting = Meeting(
            proposer_id=proposer_id,
            receiver_id=data.receiver_id,
            proposer_status=ProposalStatus.ACCEPTED,  # creator auto-joins
            receiver_status=ProposalStatus.PENDING,
            source=MeetingSource.USER,
            meeting_type=data.meeting_type,
            proposed_time=data.proposed_time,
            duration_minutes=data.duration_minutes,
            location=data.location,
            message=data.message,
        )
        meeting = await self._repo.create(meeting)
        logger.info(
            f"User {proposer_id} created meeting {meeting.id} "
            f"with {data.receiver_id}"
        )
        return meeting

    async def accept_proposal(
        self, meeting_id: uuid.UUID, user_id: uuid.UUID
    ) -> Meeting:
        """Accept a meeting proposal. The user's own status is set to accepted."""
        meeting = await self._get_meeting_for_participant(meeting_id, user_id)
        self._check_time_gate(meeting)

        if user_id == meeting.proposer_id:
            meeting.proposer_status = ProposalStatus.ACCEPTED
        else:
            meeting.receiver_status = ProposalStatus.ACCEPTED

        meeting = await self._repo.update(meeting)
        logger.info(f"User {user_id} accepted meeting {meeting_id}")
        return meeting

    async def reject_proposal(
        self, meeting_id: uuid.UUID, user_id: uuid.UUID
    ) -> Meeting:
        """Reject a meeting proposal. The user's own status is set to rejected."""
        meeting = await self._get_meeting_for_participant(meeting_id, user_id)
        self._check_time_gate(meeting)

        if user_id == meeting.proposer_id:
            meeting.proposer_status = ProposalStatus.REJECTED
        else:
            meeting.receiver_status = ProposalStatus.REJECTED

        meeting = await self._repo.update(meeting)
        logger.info(f"User {user_id} rejected meeting {meeting_id}")
        return meeting

    async def delete_meeting(
        self, meeting_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        """
        Delete a user-created meeting.
        Only the creator can delete, and only if the receiver hasn't joined.
        """
        meeting = await self._get_meeting_or_404(meeting_id)

        if meeting.source != MeetingSource.USER:
            raise PermissionError("Only user-created meetings can be deleted.")

        if meeting.proposer_id != user_id:
            raise PermissionError("Only the meeting creator can delete it.")

        if meeting.receiver_status != ProposalStatus.PENDING:
            raise PermissionError(
                "Cannot delete a meeting after the receiver has responded."
            )

        await self._repo.delete(meeting)
        logger.info(f"User {user_id} deleted meeting {meeting_id}")

    async def get_proposals(
        self,
        user_id: uuid.UUID,
        status_filter: ProposalStatus | None = None,
        role_filter: str | None = None,
    ) -> list[Meeting]:
        """List meetings involving the user, with optional filters."""
        # Lazy cleanup of expired engine meetings
        now = datetime.now(timezone.utc)
        cleaned = await self._repo.cleanup_expired_engine_meetings(now)
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} expired engine-created meetings")

        return await self._repo.list_for_user(user_id, status_filter, role_filter)

    async def get_proposal(
        self, meeting_id: uuid.UUID, user_id: uuid.UUID
    ) -> Meeting:
        """Get a single meeting by ID. User must be a participant."""
        return await self._get_meeting_for_participant(meeting_id, user_id)

    # ── Private helpers ──────────────────────────────────────

    async def _get_meeting_or_404(self, meeting_id: uuid.UUID) -> Meeting:
        meeting = await self._repo.get_by_id(meeting_id)
        if meeting is None:
            raise LookupError("Meeting not found.")
        return meeting

    async def _get_meeting_for_participant(
        self, meeting_id: uuid.UUID, user_id: uuid.UUID
    ) -> Meeting:
        meeting = await self._get_meeting_or_404(meeting_id)
        if user_id not in (meeting.proposer_id, meeting.receiver_id):
            raise PermissionError("You are not a participant in this meeting.")
        return meeting

    @staticmethod
    def _check_time_gate(meeting: Meeting) -> None:
        """
        Ensure the user can still change their status.
        Changes are blocked if the meeting starts in less than 1 hour.
        """
        if meeting.proposed_time is None:
            return  # No scheduled time — always allow changes
        now = datetime.now(timezone.utc)
        proposed = meeting.proposed_time
        # SQLite returns naive datetimes; treat them as UTC
        if proposed.tzinfo is None:
            proposed = proposed.replace(tzinfo=timezone.utc)
        if proposed - now < _STATUS_CHANGE_WINDOW:
            raise PermissionError(
                "Cannot change your status less than 1 hour before the meeting."
            )
