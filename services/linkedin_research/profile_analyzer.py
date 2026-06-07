"""Factual profile and company overview analysis."""

import re

from schemas.research_schema import INSUFFICIENT_DATA, Overview, RecentUpdate, ResearchInput
from services.linkedin_research.evidence_manager import EvidenceManager


class ProfileAnalyzer:
    """Build factual overview and recent updates from provided evidence."""

    _update_keywords = (
        "funding",
        "hiring",
        "partnership",
        "launch",
        "launched",
        "award",
        "announced",
        "product",
    )
    _timeframe_pattern = re.compile(r"\b(20\d{2}|q[1-4]\s*20\d{2}|last month|this year|recently)\b", re.IGNORECASE)

    def __init__(self, evidence_manager: EvidenceManager | None = None) -> None:
        self._evidence = evidence_manager or EvidenceManager()

    def overview(self, research_input: ResearchInput) -> Overview:
        """Return factual overview fields separated from inferred signals."""
        summary_source = self._evidence.combine_sources(
            [research_input.profile_summary, research_input.bio]
        )
        summary = self._evidence.evidence_note(summary_source) if summary_source else INSUFFICIENT_DATA
        return Overview(
            summary=summary,
            role=research_input.role_title,
            company=research_input.normalized_company_name or research_input.company_name,
            industry=research_input.industry or INSUFFICIENT_DATA,
        )

    def recent_updates(self, research_input: ResearchInput) -> list[RecentUpdate]:
        """Return evidence-backed recent company/news updates."""
        updates: list[RecentUpdate] = []
        for update in research_input.company_updates:
            sanitized = self._evidence.sanitize_text(update)
            if not self._contains_update_signal(sanitized):
                continue
            timeframe_match = self._timeframe_pattern.search(sanitized)
            updates.append(
                RecentUpdate(
                    update=self._evidence.evidence_note(sanitized),
                    evidence=self._evidence.evidence_note(sanitized),
                    date_or_timeframe=timeframe_match.group(0) if timeframe_match else INSUFFICIENT_DATA,
                )
            )

        return updates or [RecentUpdate()]

    def person_evidence(self, research_input: ResearchInput) -> str:
        """Return combined person-level evidence."""
        return self._evidence.combine_sources(
            [research_input.profile_summary, research_input.bio, *research_input.posts, *research_input.interviews]
        )

    def company_evidence(self, research_input: ResearchInput) -> str:
        """Return combined company-level evidence."""
        return self._evidence.combine_sources([research_input.company_content, *research_input.company_updates])

    def _contains_update_signal(self, text: str) -> bool:
        """Return True when company text contains an allowed update category."""
        normalized = text.casefold()
        return any(keyword in normalized for keyword in self._update_keywords)
