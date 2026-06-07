"""Company news and growth signal extraction."""

import re

from schemas.companyResearchSchema import ApprovedCompanySource, CompanyRecentUpdate
from schemas.companyResearchSchema import INSUFFICIENT_DATA
from services.linkedin_research.evidence_manager import EvidenceManager


class CompanyNewsExtractor:
    """Extract factual recent updates and growth/hiring signals."""

    _update_keywords = (
        "launch",
        "launched",
        "funding",
        "raised",
        "partnership",
        "partnered",
        "acquisition",
        "acquired",
        "expansion",
        "expanded",
        "award",
        "announced",
    )
    _growth_keywords = ("hiring", "expanding", "growth", "scaling", "recruiting", "new roles", "open positions")
    _timeframe_pattern = re.compile(r"\b(20\d{2}|q[1-4]\s*20\d{2}|recently|this year|last month|today)\b", re.IGNORECASE)

    def __init__(self, evidence_manager: EvidenceManager | None = None) -> None:
        self._evidence = evidence_manager or EvidenceManager()

    def recent_updates(self, sources: list[ApprovedCompanySource]) -> list[CompanyRecentUpdate]:
        """Return factual recent updates only when source text supports them."""
        updates: list[CompanyRecentUpdate] = []
        for source in sources:
            text = self._evidence.sanitize_text(source.text)
            if not text or not any(keyword in text.casefold() for keyword in self._update_keywords):
                continue
            timeframe_match = self._timeframe_pattern.search(text)
            updates.append(
                CompanyRecentUpdate(
                    update=self._evidence.evidence_note(text),
                    evidence=self._evidence.evidence_note(text),
                    source_type=source.source_type,
                    date_or_timeframe=source.date_or_timeframe
                    if source.date_or_timeframe != INSUFFICIENT_DATA
                    else (timeframe_match.group(0) if timeframe_match else INSUFFICIENT_DATA),
                )
            )
            if len(updates) == 3:
                break
        return updates

    def growth_or_hiring_signal(self, sources: list[ApprovedCompanySource]) -> str:
        """Return growth or hiring signal when evidence supports it."""
        for source in sources:
            text = self._evidence.sanitize_text(source.text)
            if any(keyword in text.casefold() for keyword in self._growth_keywords):
                return self._evidence.evidence_note(text)
        return INSUFFICIENT_DATA
