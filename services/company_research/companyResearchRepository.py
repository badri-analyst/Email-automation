"""Campaign-level company research repository abstraction."""

from schemas.companyResearchSchema import CompanyResearchOutput


class CompanyResearchRepository:
    """In-memory repository for duplicate company research within a campaign run."""

    def __init__(self) -> None:
        self._store: dict[tuple[str, str], CompanyResearchOutput] = {}

    def get(self, campaign_id: str, company_name_cleaned: str) -> CompanyResearchOutput | None:
        """Return cached research output for a campaign/company pair."""
        return self._store.get((campaign_id, company_name_cleaned.casefold()))

    def save(self, campaign_id: str, company_name_cleaned: str, output: CompanyResearchOutput) -> None:
        """Cache research output for a campaign/company pair."""
        self._store[(campaign_id, company_name_cleaned.casefold())] = output
