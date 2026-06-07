"""Observable professional motivator extraction."""

from schemas.personalityAnalysisSchema import ProfessionalMotivatorOutput
from services.linkedin_research.evidence_manager import EvidenceManager


class ProfessionalMotivatorExtractor:
    """Extract allowed professional motivators only when evidence exists."""

    _motivators = {
        "Innovation / curiosity": ("innovation", "curious", "ai", "automation", "new product"),
        "Growth / business results": ("growth", "revenue", "business results", "scale"),
        "Impact / mission": ("impact", "mission", "outcomes", "purpose"),
        "Efficiency / process improvement": ("efficiency", "process improvement", "workflow", "streamline"),
        "Security / stability": ("security", "stability", "governance", "compliance"),
        "Recognition / credibility": ("recognized", "award", "featured", "speaker"),
        "Customer value": ("customer value", "customer", "client", "user experience"),
        "Team collaboration": ("team", "collaboration", "cross-functional", "stakeholder"),
        "Delivery excellence": ("delivery", "quality", "execution", "launched"),
    }

    def __init__(self, evidence_manager: EvidenceManager | None = None) -> None:
        self._evidence = evidence_manager or EvidenceManager()

    def extract(self, text: str) -> list[ProfessionalMotivatorOutput]:
        """Return supported motivators."""
        if not self._evidence.has_evidence(text):
            return []

        normalized = text.casefold()
        results: list[ProfessionalMotivatorOutput] = []
        for motivator, keywords in self._motivators.items():
            if any(keyword in normalized for keyword in keywords):
                results.append(
                    ProfessionalMotivatorOutput(
                        motivator=motivator,
                        why=f"Provided professional content references {motivator.casefold()} themes.",
                        evidence=self._evidence.evidence_note(text),
                    )
                )
            if len(results) == 5:
                break
        return results
