"""
Profile service — business logic for viewing and updating user profiles.
"""

import logging
import uuid

from icebreakers.profile.domain.models import Profile
from icebreakers.profile.domain.schemas import ProfileUpdateRequest
from icebreakers.profile.infrastructure.repository import ProfileRepository

logger = logging.getLogger("icebreakers")


class ProfileService:
    def __init__(self, repo: ProfileRepository) -> None:
        self._repo = repo

    async def get_profile(self, user_id: uuid.UUID) -> Profile:
        """
        Return the profile for the given user.
        If no profile exists yet, lazily create an empty one.
        """
        profile = await self._repo.get_by_user_id(user_id)
        if profile is None:
            logger.info(f"Auto-creating empty profile for user {user_id}")
            profile = Profile(user_id=user_id)
            profile = await self._repo.create(profile)
        return profile

    async def update_profile(
        self, user_id: uuid.UUID, data: ProfileUpdateRequest
    ) -> Profile:
        """
        Update the profile fields that are provided (non-None) in the request.
        Preserves existing values for fields not included in the update.
        """
        profile = await self.get_profile(user_id)

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)

        profile = await self._repo.update(profile)
        logger.info(f"Updated profile for user {user_id}")
        return profile

    @staticmethod
    def is_profile_complete(profile: Profile) -> bool:
        """
        A profile is considered complete when all required fields are filled:
        - first_name is non-empty
        - last_name is non-empty
        - bio is non-empty
        - interests has at least 1 entry
        """
        if not profile.first_name:
            return False
        if not profile.last_name:
            return False
        if not profile.bio:
            return False
        if not profile.interests or len(profile.interests) == 0:
            return False
        return True
