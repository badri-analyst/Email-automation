"""Professional motivator extraction."""

from schemas.research_schema import ProfessionalMotivator
from services.linkedin_research.evidence_manager import EvidenceManager


class MotivatorAnalyzer:
    """Infer allowed professional motivators only when text evidence exists."""

    _motivator_keywords = {
        "innovation": ("innovation", "new product", "ai", "automation", "modernize"),
        "growth": ("growth", "scale", "expansion", "revenue", "pipeline"),
        "impact": ("impact", "outcomes", "results", "mission"),
        "efficiency": ("efficiency", "process", "productivity", "streamline", "optimize"),
        "customer value": ("customer value", "customer", "client", "user experience"),
        "collaboration": ("collaboration", "team", "cross-functional", "partnership"),
        "recognition": ("award", "recognized", "featured", "speaker"),
        "stability": ("reliability", "governance", "compliance", "secure", "resilience"),
    }

    def __init__(self, evidence_manager: EvidenceManager | None = None) -> None:
        self._evidence = evidence_manager or EvidenceManager()

    def analyze(self, text: str) -> list[ProfessionalMotivator]:
        """Return supported professional motivators."""
        if not self._evidence.has_evidence(text):
            return []

        normalized = text.casefold()
        motivators: list[ProfessionalMotivator] = []
        for motivator, keywords in self._motivator_keywords.items():
            if any(keyword in normalized for keyword in keywords):
                motivators.append(
                    ProfessionalMotivator(
                        motivator=motivator,
                        why=f"Provided professional text references {motivator} themes.",
                        evidence=self._evidence.evidence_note(text),
                    )
                )
            if len(motivators) == 4:
                break
        return motivators
