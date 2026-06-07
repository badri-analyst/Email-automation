"""Company values and culture signal extraction."""

from schemas.companyResearchSchema import ApprovedCompanySource
from schemas.companyResearchSchema import INSUFFICIENT_DATA
from services.linkedin_research.evidence_manager import EvidenceManager


class CompanyValuesExtractor:
    """Extract company values/culture signals from approved company sources."""

    _value_keywords = (
        "values",
        "culture",
        "collaboration",
        "customer",
        "innovation",
        "diversity",
        "inclusion",
        "ownership",
        "integrity",
        "mission",
    )

    def __init__(self, evidence_manager: EvidenceManager | None = None) -> None:
        self._evidence = evidence_manager or EvidenceManager()

    def values_summary(self, sources: list[ApprovedCompanySource]) -> str:
        """Return values/culture summary only when source text supports it."""
        for source in sources:
            text = self._evidence.sanitize_text(source.text)
            if any(keyword in text.casefold() for keyword in self._value_keywords):
                return self._evidence.evidence_note(text)
        return INSUFFICIENT_DATA
