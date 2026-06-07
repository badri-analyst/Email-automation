"""Campaign-level professional communication analysis repository."""

from schemas.personalityAnalysisSchema import PersonalityAnalysisOutput


class PersonalityAnalysisRepository:
    """In-memory cache for duplicate professional communication analysis."""

    def __init__(self) -> None:
        self._store: dict[tuple[str, str, str, str], PersonalityAnalysisOutput] = {}

    def get(self, campaign_id: str, person_name: str, job_title: str, company_name: str) -> PersonalityAnalysisOutput | None:
        """Return cached analysis."""
        return self._store.get(self._key(campaign_id, person_name, job_title, company_name))

    def save(
        self,
        campaign_id: str,
        person_name: str,
        job_title: str,
        company_name: str,
        output: PersonalityAnalysisOutput,
    ) -> None:
        """Cache analysis."""
        self._store[self._key(campaign_id, person_name, job_title, company_name)] = output

    @staticmethod
    def _key(campaign_id: str, person_name: str, job_title: str, company_name: str) -> tuple[str, str, str, str]:
        """Return deterministic cache key."""
        return (campaign_id, person_name.casefold(), job_title.casefold(), company_name.casefold())
