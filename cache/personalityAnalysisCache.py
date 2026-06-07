"""Campaign-level personality-safe analysis cache facade."""

from schemas.personalityAnalysisSchema import PersonalityAnalysisOutput
from services.personality_analysis.personalityAnalysisRepository import PersonalityAnalysisRepository


class PersonalityAnalysisCache:
    """Cache facade for duplicate communication analysis."""

    def __init__(self) -> None:
        self._repository = PersonalityAnalysisRepository()

    @property
    def repository(self) -> PersonalityAnalysisRepository:
        """Return repository for dependency injection."""
        return self._repository

    def get(self, campaign_id: str, person_name: str, job_title: str, company_name: str) -> PersonalityAnalysisOutput | None:
        """Return cached analysis."""
        return self._repository.get(campaign_id, person_name, job_title, company_name)

    def save(
        self,
        campaign_id: str,
        person_name: str,
        job_title: str,
        company_name: str,
        output: PersonalityAnalysisOutput,
    ) -> None:
        """Save analysis in cache."""
        self._repository.save(campaign_id, person_name, job_title, company_name, output)
