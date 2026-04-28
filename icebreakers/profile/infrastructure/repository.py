"""
Profile repository — data-access layer for the Profile model.
Abstracts raw SQL/ORM queries from the rest of the application.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from icebreakers.profile.domain.models import Profile


class ProfileRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_user_id(self, user_id: uuid.UUID) -> Profile | None:
        result = await self._db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, profile: Profile) -> Profile:
        self._db.add(profile)
        await self._db.flush()
        await self._db.refresh(profile)
        return profile

    async def update(self, profile: Profile) -> Profile:
        """Merge the modified profile back into the session."""
        merged = await self._db.merge(profile)
        await self._db.flush()
        await self._db.refresh(merged)
        return merged
