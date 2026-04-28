"""
Profile API router — get and update user profile.
Requires authentication via HttpOnly cookie (architecture §3.4).
"""

from fastapi import APIRouter, Depends, Request

from icebreakers.auth.domain.models import User
from icebreakers.profile.application.service import ProfileService
from icebreakers.profile.domain.schemas import (
    ProfileResponse,
    ProfileUpdateRequest,
)
from icebreakers.shared.dependencies import (
    get_current_user,
    get_profile_service,
    verify_csrf,
)
from icebreakers.shared.rate_limit import limiter

router = APIRouter(prefix="/api/profile", tags=["profile"])

@router.get(
    "",
    response_model=ProfileResponse,
    summary="Get current user's profile",
)
async def get_profile(
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> ProfileResponse:
    """Return the authenticated user's profile. Auto-creates if absent."""
    profile = await profile_service.get_profile(current_user.id)
    return ProfileResponse(
        **{
            "id": profile.id,
            "user_id": profile.user_id,
            "first_name": profile.first_name,
            "middle_name": profile.middle_name,
            "last_name": profile.last_name,
            "bio": profile.bio,
            "interests": profile.interests,
            "avatar_url": profile.avatar_url,
            "location": profile.location,
            "is_profile_complete": ProfileService.is_profile_complete(profile),
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
        }
    )


@router.put(
    "",
    response_model=ProfileResponse,
    summary="Update current user's profile",
    dependencies=[Depends(verify_csrf)],
)
@limiter.limit("30/minute")
async def update_profile(
    request: Request,
    data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(get_profile_service),
) -> ProfileResponse:
    """Update the authenticated user's profile with the provided fields."""
    profile = await profile_service.update_profile(current_user.id, data)
    return ProfileResponse(
        **{
            "id": profile.id,
            "user_id": profile.user_id,
            "first_name": profile.first_name,
            "middle_name": profile.middle_name,
            "last_name": profile.last_name,
            "bio": profile.bio,
            "interests": profile.interests,
            "avatar_url": profile.avatar_url,
            "location": profile.location,
            "is_profile_complete": ProfileService.is_profile_complete(profile),
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
        }
    )
