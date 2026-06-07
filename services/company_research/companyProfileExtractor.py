"""Company profile extraction from approved source snippets."""

from schemas.companyResearchSchema import ApprovedCompanySource
from schemas.companyResearchSchema import INSUFFICIENT_DATA
from services.linkedin_research.evidence_manager import EvidenceManager


class CompanyProfileExtractor:
    """Extract factual company overview, industry, and product/service context."""

    _industry_keywords = {
        "software": ("software", "saas", "platform", "cloud"),
        "financial services": ("finance", "banking", "payments", "fintech"),
        "healthcare": ("healthcare", "medical", "clinical", "patient"),
        "education": ("education", "learning", "students", "training"),
        "ecommerce": ("commerce", "retail", "marketplace", "shopping"),
        "manufacturing": ("manufacturing", "industrial", "factory", "supply chain"),
        "consulting": ("consulting", "advisory", "services firm"),
    }
    _product_keywords = ("product", "platform", "service", "solution", "tool", "software", "app")

    def __init__(self, evidence_manager: EvidenceManager | None = None) -> None:
        self._evidence = evidence_manager or EvidenceManager()

    def overview(self, sources: list[ApprovedCompanySource]) -> str:
        """Return a factual company overview or insufficient-data marker."""
        text = self._combined_text(sources)
        return self._evidence.evidence_note(text) if self._evidence.has_evidence(text) else INSUFFICIENT_DATA

    def industry(self, sources: list[ApprovedCompanySource]) -> str:
        """Return industry/domain when source text supports it."""
        text = self._combined_text(sources).casefold()
        for industry, keywords in self._industry_keywords.items():
            if any(keyword in text for keyword in keywords):
                return industry
        return INSUFFICIENT_DATA

    def products_services(self, sources: list[ApprovedCompanySource]) -> str:
        """Return products/services summary when observable evidence exists."""
        text = self._combined_text(sources)
        normalized = text.casefold()
        if not any(keyword in normalized for keyword in self._product_keywords):
            return INSUFFICIENT_DATA
        return self._evidence.evidence_note(text)

    def _combined_text(self, sources: list[ApprovedCompanySource]) -> str:
        """Return sanitized source text."""
        return self._evidence.combine_sources([source.text for source in sources])
