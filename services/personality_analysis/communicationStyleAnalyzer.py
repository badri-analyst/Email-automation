"""Rule-based professional communication style analysis."""

from schemas.personalityAnalysisSchema import (
    CommunicationStyleOutput,
    INSUFFICIENT_DATA,
)
from services.linkedin_research.evidence_manager import EvidenceManager


class CommunicationStyleAnalyzer:
    """Analyze observable communication style from professional content."""

    _tone_keywords = {
        "Technical": ("api", "architecture", "data", "engineering", "system", "automation"),
        "Educational": ("learn", "guide", "framework", "explains", "lesson", "how to"),
        "Authoritative": ("leader", "strategy", "decision", "executive", "governance"),
        "Friendly": ("thanks", "excited", "grateful", "team", "together"),
        "Direct": ("must", "need", "clear", "focus", "priority"),
        "Formal": ("governance", "compliance", "policy", "documentation"),
        "Professional": ("stakeholder", "business", "delivery", "outcomes"),
        "Casual": ("quick", "sharing", "thoughts", "nice"),
    }
    _structure_keywords = {
        "Data-heavy": ("data", "metrics", "measured", "analysis", "kpi"),
        "Storytelling": ("when", "journey", "story", "learned", "experience"),
        "Educational": ("how to", "guide", "framework", "lesson"),
        "Practical": ("steps", "process", "workflow", "example", "template"),
        "Announcement-style": ("announced", "launch", "new role", "excited to share"),
        "Opinion-led": ("i believe", "point of view", "opinion", "should"),
        "Long-form": ("first", "second", "finally", "in conclusion"),
        "Short-form": ("quick update", "brief", "short"),
    }
    _energy_keywords = {
        "High-energy": ("thrilled", "amazing", "huge", "incredible"),
        "Enthusiastic": ("excited", "proud", "delighted", "looking forward"),
        "Assertive": ("must", "critical", "essential", "priority"),
        "Persuasive": ("why", "because", "should", "important"),
        "Reflective": ("learned", "reflection", "consider", "thoughtful"),
        "Calm": ("steady", "careful", "measured", "clear"),
        "Neutral": ("update", "shared", "noted"),
    }
    _audience_keywords = {
        "recruiters": ("recruiter", "hiring", "talent"),
        "executives": ("executive", "leadership", "board", "c-suite"),
        "developers": ("developer", "engineer", "api", "code"),
        "founders": ("founder", "startup", "venture"),
        "customers": ("customer", "client", "user"),
        "hiring teams": ("hiring team", "interview", "role"),
        "general business audience": ("business", "stakeholder", "market"),
    }

    def __init__(self, evidence_manager: EvidenceManager | None = None) -> None:
        self._evidence = evidence_manager or EvidenceManager()

    def analyze(self, text: str) -> CommunicationStyleOutput:
        """Return evidence-backed communication style."""
        if not self._evidence.has_evidence(text):
            return CommunicationStyleOutput()

        normalized = text.casefold()
        return CommunicationStyleOutput(
            tone=self._match(normalized, self._tone_keywords, "Neutral"),
            structure=self._match(normalized, self._structure_keywords, "Insufficient data"),
            energy=self._match(normalized, self._energy_keywords, "Neutral"),
            audience_focus=self._match(normalized, self._audience_keywords, INSUFFICIENT_DATA),
            evidence=self._evidence.evidence_note(text),
        )

    @staticmethod
    def _match(text: str, keyword_map: dict[str, tuple[str, ...]], fallback: str) -> str:
        """Return first matching configured category."""
        for label, keywords in keyword_map.items():
            if any(keyword in text for keyword in keywords):
                return label
        return fallback
