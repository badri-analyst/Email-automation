"""Communication style and professional signal analysis."""

from schemas.research_schema import (
    INSUFFICIENT_DATA,
    CommunicationStyle,
    ProfessionalBehavioralSignal,
)
from services.linkedin_research.evidence_manager import EvidenceManager


class CommunicationAnalyzer:
    """Extract communication style and allowed behavioral signals from evidence."""

    _tone_keywords = {
        "technical": ("architecture", "system", "engineering", "data", "api", "automation"),
        "collaborative": ("team", "collaborate", "partnership", "cross-functional", "together"),
        "customer-focused": ("customer", "client", "user", "experience"),
        "business-focused": ("growth", "revenue", "market", "strategy", "business"),
    }
    _behavior_keywords = {
        "analytical": ("analysis", "data", "metrics", "research", "evidence"),
        "detail-oriented": ("process", "documentation", "quality", "compliance", "precision"),
        "big-picture": ("vision", "strategy", "roadmap", "transformation"),
        "technical": ("engineering", "architecture", "developer", "software", "platform"),
        "business-focused": ("revenue", "market", "customers", "sales", "growth"),
        "strategic": ("strategy", "vision", "long-term", "roadmap"),
        "execution-focused": ("delivered", "launched", "implemented", "built", "shipped"),
        "value-driven": ("impact", "outcomes", "customer value", "efficiency"),
    }

    def __init__(self, evidence_manager: EvidenceManager | None = None) -> None:
        self._evidence = evidence_manager or EvidenceManager()

    def analyze_style(self, text: str) -> CommunicationStyle:
        """Return evidence-backed communication style."""
        if not self._evidence.has_evidence(text):
            return CommunicationStyle()

        normalized = text.casefold()
        tone = self._first_matching_label(normalized, self._tone_keywords) or INSUFFICIENT_DATA
        structure = "structured" if any(word in normalized for word in ("first", "second", "framework", "process")) else INSUFFICIENT_DATA
        energy = "active" if any(word in normalized for word in ("launched", "built", "delivered", "driving")) else INSUFFICIENT_DATA
        audience_focus = (
            "customer or user focused"
            if any(word in normalized for word in ("customer", "client", "user", "audience"))
            else INSUFFICIENT_DATA
        )

        return CommunicationStyle(
            tone=tone,
            structure=structure,
            energy=energy,
            audience_focus=audience_focus,
            evidence=self._evidence.evidence_note(text),
        )

    def behavioral_signals(self, text: str) -> list[ProfessionalBehavioralSignal]:
        """Return allowed behavioral signals only when evidence exists."""
        if not self._evidence.has_evidence(text):
            return []

        normalized = text.casefold()
        signals: list[ProfessionalBehavioralSignal] = []
        for signal, keywords in self._behavior_keywords.items():
            if any(keyword in normalized for keyword in keywords):
                signals.append(
                    ProfessionalBehavioralSignal(
                        signal=signal,
                        explanation=f"Professional text references {signal.replace('-', ' ')} work patterns.",
                        evidence=self._evidence.evidence_note(text),
                    )
                )
            if len(signals) == 4:
                break
        return signals

    @staticmethod
    def _first_matching_label(text: str, keyword_map: dict[str, tuple[str, ...]]) -> str | None:
        """Return the first label with keyword evidence."""
        for label, keywords in keyword_map.items():
            if any(keyword in text for keyword in keywords):
                return label
        return None
