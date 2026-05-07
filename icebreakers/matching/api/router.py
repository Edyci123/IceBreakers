from fastapi import APIRouter, Depends, HTTPException, status

from icebreakers.auth.domain.models import User
from icebreakers.auth.domain.enums import UserRole
from icebreakers.shared.dependencies import get_current_user, get_matching_service
from icebreakers.matching.application.service import MatchingService

router = APIRouter(prefix="/matching", tags=["matching"])

def require_admin(user: User = Depends(get_current_user)) -> User:
    """Dependency to enforce Admin role."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Requires admin privileges."
        )
    return user

@router.post("/trigger", status_code=status.HTTP_200_OK)
async def trigger_matching(
    current_admin: User = Depends(require_admin),
    service: MatchingService = Depends(get_matching_service)
):
    """
    Trigger the generation of new user match proposals based on semantic distance.
    Requires Admin privileges.
    """
    count = await service.trigger_matching()
    return {"message": "Matching triggered successfully", "proposals_created": count}
