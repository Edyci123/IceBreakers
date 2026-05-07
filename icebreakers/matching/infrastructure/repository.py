import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from icebreakers.matching.domain.models import Proposal
from icebreakers.profile.domain.models import Profile
from icebreakers.auth.domain.models import User


class MatchingRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_all_active_profiles(self) -> list[Profile]:
        """Fetch all profiles belonging to active users."""
        result = await self._db.execute(
            select(Profile)
            .join(User, Profile.user_id == User.id)
            .where(User.is_active == True)
        )
        return list(result.scalars().all())

    async def get_existing_proposal_pairs(self) -> set[frozenset[uuid.UUID]]:
        """Return a set of frozensets containing existing user pairs."""
        result = await self._db.execute(select(Proposal.user_a_id, Proposal.user_b_id))
        pairs = set()
        for row in result.all():
            pairs.add(frozenset([row.user_a_id, row.user_b_id]))
        return pairs

    async def save_proposals(self, proposals: list[Proposal]) -> None:
        """Save a batch of proposals to the database."""
        if not proposals:
            return
        self._db.add_all(proposals)
        await self._db.flush()
