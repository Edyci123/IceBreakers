import uuid

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from icebreakers.matching.domain.models import Proposal
from icebreakers.matching.infrastructure.repository import MatchingRepository
from icebreakers.profile.domain.models import Profile


class MatchingService:
    def __init__(self, repository: MatchingRepository) -> None:
        self._repository = repository

    def _prepare_documents(self, profiles: list[Profile]) -> list[str]:
        """Combine bio and interests into a single text document per profile."""
        docs = []
        for p in profiles:
            bio = p.bio or ""
            interests = " ".join(p.interests) if p.interests else ""
            doc_text = f"{bio} {interests}".strip()
            # Prevent empty documents from breaking TfidfVectorizer
            if not doc_text:
                doc_text = "no_information_provided"
            docs.append(doc_text)
        return docs

    async def trigger_matching(self) -> int:
        """
        Main logic for computing semantic matching using TF-IDF and Cosine Similarity.
        Returns the number of proposals created.
        """
        profiles = await self._repository.get_all_active_profiles()
        if len(profiles) < 2:
            return 0

        existing_pairs = await self._repository.get_existing_proposal_pairs()
        docs = self._prepare_documents(profiles)

        try:
            vectorizer = TfidfVectorizer(stop_words="english")
            tfidf_matrix = vectorizer.fit_transform(docs)
            similarity_matrix = cosine_similarity(tfidf_matrix)
        except ValueError:
            # Fallback if vocabulary is completely empty or invalid
            similarity_matrix = np.zeros((len(profiles), len(profiles)))

        n = len(profiles)
        pairs_sim = []
        for i in range(n):
            for j in range(i + 1, n):
                pairs_sim.append((similarity_matrix[i, j], i, j))

        # Sort pairs by similarity, highest first
        pairs_sim.sort(key=lambda x: x[0], reverse=True)

        matched_indices = set()
        new_proposals = []

        for sim, i, j in pairs_sim:
            if i in matched_indices or j in matched_indices:
                continue

            user_a_id = profiles[i].user_id
            user_b_id = profiles[j].user_id

            pair_set = frozenset([user_a_id, user_b_id])
            if pair_set in existing_pairs:
                continue

            matched_indices.add(i)
            matched_indices.add(j)

            proposal = Proposal(
                user_a_id=user_a_id,
                user_b_id=user_b_id
            )
            new_proposals.append(proposal)

        await self._repository.save_proposals(new_proposals)
        return len(new_proposals)
