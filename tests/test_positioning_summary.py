"""Tests for candidate positioning summaries."""

from services.candidate_assets.positioningSummaryBuilder import PositioningSummaryBuilder
from services.candidate_assets.whyRelevantBuilder import WhyRelevantBuilder


def test_positioning_summary_uses_candidate_provided_text() -> None:
    """Positioning summary should use candidate-provided factual text."""
    summary = PositioningSummaryBuilder().build(
        "IT Business Analyst focused on workflow clarity and stakeholder alignment",
        "Business Analyst",
        "",
    )

    assert summary == "IT Business Analyst focused on workflow clarity and stakeholder alignment"


def test_why_relevant_summary_is_low_pressure() -> None:
    """Why relevant summary should avoid hire-me framing."""
    summary = WhyRelevantBuilder().build(["requirements clarification example"], "")

    assert summary.startswith("May be relevant")
    assert "hire me" not in summary.casefold()
