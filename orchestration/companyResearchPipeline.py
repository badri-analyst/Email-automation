"""Batch orchestration for company-level research."""

from schemas.companyResearchSchema import CompanyResearchInput, CompanyResearchOutput
from services.company_research.companyResearchController import CompanyResearchController
from services.company_research.companyResearchRepository import CompanyResearchRepository


class CompanyResearchPipeline:
    """Batch company research pipeline with campaign-level duplicate caching."""

    def __init__(self, repository: CompanyResearchRepository | None = None) -> None:
        self._repository = repository or CompanyResearchRepository()
        self._controller = CompanyResearchController(repository=self._repository)

    def research_company(self, payload: CompanyResearchInput | dict[str, object]) -> CompanyResearchOutput:
        """Research one company safely."""
        return self._controller.research(payload)

    def research_batch(self, payloads: list[CompanyResearchInput | dict[str, object]]) -> list[CompanyResearchOutput]:
        """Research multiple companies while isolating per-company failures."""
        return [self.research_company(payload) for payload in payloads]
