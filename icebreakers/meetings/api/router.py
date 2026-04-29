"""
Meetings API router — create, list, accept, reject, delete meeting proposals.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from icebreakers.auth.domain.models import User
from icebreakers.meetings.application.service import MeetingService
from icebreakers.meetings.domain.enums import ProposalStatus
from icebreakers.meetings.domain.models import Meeting
from icebreakers.meetings.domain.schemas import (
    MeetingCreateRequest,
    MeetingResponse,
)
from icebreakers.shared.dependencies import (
    get_current_user,
    get_meeting_service,
    verify_csrf,
)
from icebreakers.shared.rate_limit import limiter

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


def _to_response(meeting: Meeting) -> MeetingResponse:
    """Convert a Meeting ORM object to a MeetingResponse, loading emails."""
    return MeetingResponse(
        id=meeting.id,
        proposer_id=meeting.proposer_id,
        receiver_id=meeting.receiver_id,
        proposer_status=meeting.proposer_status,
        receiver_status=meeting.receiver_status,
        source=meeting.source,
        meeting_type=meeting.meeting_type,
        proposed_time=meeting.proposed_time,
        duration_minutes=meeting.duration_minutes,
        location=meeting.location,
        message=meeting.message,
        proposer_email=meeting.proposer.email if meeting.proposer else "",
        receiver_email=meeting.receiver.email if meeting.receiver else "",
        created_at=meeting.created_at,
        updated_at=meeting.updated_at,
    )


@router.post(
    "/proposals",
    response_model=MeetingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new meeting proposal",
    dependencies=[Depends(verify_csrf)],
)
@limiter.limit("20/minute")
async def create_proposal(
    request: Request,
    data: MeetingCreateRequest,
    current_user: User = Depends(get_current_user),
    meeting_service: MeetingService = Depends(get_meeting_service),
) -> MeetingResponse:
    try:
        meeting = await meeting_service.create_proposal(current_user.id, data)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        )
    return _to_response(meeting)


@router.get(
    "/proposals",
    response_model=list[MeetingResponse],
    summary="List meeting proposals for the current user",
)
async def list_proposals(
    current_user: User = Depends(get_current_user),
    meeting_service: MeetingService = Depends(get_meeting_service),
    status_filter: ProposalStatus | None = Query(
        default=None,
        alias="status",
        description="Filter by your status in the meeting",
    ),
    role: str | None = Query(
        default=None,
        description="Filter by role: 'proposer' or 'receiver'",
        pattern="^(proposer|receiver)$",
    ),
) -> list[MeetingResponse]:
    meetings = await meeting_service.get_proposals(
        current_user.id, status_filter, role
    )
    return [_to_response(m) for m in meetings]


@router.get(
    "/proposals/{meeting_id}",
    response_model=MeetingResponse,
    summary="Get a single meeting proposal",
)
async def get_proposal(
    meeting_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    meeting_service: MeetingService = Depends(get_meeting_service),
) -> MeetingResponse:
    try:
        meeting = await meeting_service.get_proposal(meeting_id, current_user.id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        )
    return _to_response(meeting)


@router.put(
    "/proposals/{meeting_id}/accept",
    response_model=MeetingResponse,
    summary="Accept a meeting proposal",
    dependencies=[Depends(verify_csrf)],
)
async def accept_proposal(
    meeting_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    meeting_service: MeetingService = Depends(get_meeting_service),
) -> MeetingResponse:
    try:
        meeting = await meeting_service.accept_proposal(meeting_id, current_user.id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        )
    return _to_response(meeting)


@router.put(
    "/proposals/{meeting_id}/reject",
    response_model=MeetingResponse,
    summary="Reject a meeting proposal",
    dependencies=[Depends(verify_csrf)],
)
async def reject_proposal(
    meeting_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    meeting_service: MeetingService = Depends(get_meeting_service),
) -> MeetingResponse:
    try:
        meeting = await meeting_service.reject_proposal(meeting_id, current_user.id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        )
    return _to_response(meeting)


@router.delete(
    "/proposals/{meeting_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user-created meeting (only if receiver hasn't joined)",
    dependencies=[Depends(verify_csrf)],
)
async def delete_proposal(
    meeting_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    meeting_service: MeetingService = Depends(get_meeting_service),
) -> None:
    try:
        await meeting_service.delete_meeting(meeting_id, current_user.id)
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        )
