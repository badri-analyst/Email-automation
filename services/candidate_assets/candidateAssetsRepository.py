"""Candidate assets repository."""

from schemas.candidateAssetsSchema import CandidateAssetsOutput


class CandidateAssetsRepository:
    """In-memory cache for candidate proof metadata."""

    def __init__(self) -> None:
        self._store: dict[tuple[str, str], CandidateAssetsOutput] = {}

    def get(self, campaign_id: str, candidate_id: str) -> CandidateAssetsOutput | None:
        """Return cached assets output."""
        return self._store.get((campaign_id, candidate_id))

    def save(self, output: CandidateAssetsOutput) -> None:
        """Save assets output."""
        self._store[(output.campaign_id, output.candidate_id)] = output
