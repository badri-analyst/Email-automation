"""Observable professional signal extraction."""

from schemas.personalityAnalysisSchema import ProfessionalBehavioralSignalOutput
from services.linkedin_research.evidence_manager import EvidenceManager


class ProfessionalSignalExtractor:
    """Extract allowed professional signals only when evidence exists."""

    _signals = {
        "Analytical": ("analysis", "data", "metrics", "evidence", "research"),
        "Detail-oriented": ("detail", "documentation", "quality", "precision", "requirements"),
        "Big-picture": ("strategy", "vision", "roadmap", "transformation"),
        "Risk-taking": ("experiment", "new market", "bold", "startup"),
        "Conservative": ("governance", "compliance", "stability", "risk control"),
        "Strategic": ("strategy", "priorities", "long-term", "direction"),
        "Execution-focused": ("delivered", "launched", "implemented", "shipped"),
        "Technical": ("engineering", "api", "architecture", "software", "automation"),
        "Business-focused": ("revenue", "market", "business", "growth"),
        "Value-driven": ("impact", "outcomes", "customer value", "results"),
        "Self-promotional": ("featured", "award", "recognized", "speaker"),
        "Collaborative": ("collaboration", "team", "cross-functional", "stakeholders"),
        "Customer-focused": ("customer", "client", "user experience"),
        "Innovation-focused": ("innovation", "ai", "automation", "new product"),
        "Process-focused": ("process", "workflow", "operating model", "efficiency"),
    }

    def __init__(self, evidence_manager: EvidenceManager | None = None) -> None:
        self._evidence = evidence_manager or EvidenceManager()

    def extract(self, text: str) -> list[ProfessionalBehavioralSignalOutput]:
        """Return supported professional signals."""
        if not self._evidence.has_evidence(text):
            return []

        normalized = text.casefold()
        results: list[ProfessionalBehavioralSignalOutput] = []
        for signal, keywords in self._signals.items():
            if any(keyword in normalized for keyword in keywords):
                results.append(
                    ProfessionalBehavioralSignalOutput(
                        signal=signal,
                        explanation=f"Professional content references {signal.casefold()} work patterns.",
                        evidence=self._evidence.evidence_note(text),
                    )
                )
            if len(results) == 5:
                break
        return results
