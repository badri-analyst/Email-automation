"""Campaign company cache facade."""

from schemas.companyResearchSchema import CompanyResearchOutput
from services.company_research.companyResearchRepository import CompanyResearchRepository


class CampaignCompanyCache:
    """Small facade over the company research repository for campaign execution."""

    def __init__(self) -> None:
        self._repository = CompanyResearchRepository()

    @property
    def repository(self) -> CompanyResearchRepository:
        """Return the underlying repository for dependency injection."""
        return self._repository

    def get(self, campaign_id: str, company_name_cleaned: str) -> CompanyResearchOutput | None:
        """Return cached company research if available."""
        return self._repository.get(campaign_id, company_name_cleaned)

    def save(self, campaign_id: str, company_name_cleaned: str, output: CompanyResearchOutput) -> None:
        """Persist company research in campaign memory."""
        self._repository.save(campaign_id, company_name_cleaned, output)
