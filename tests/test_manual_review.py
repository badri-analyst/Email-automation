"""Tests for decision manual review logic."""

from services.decision_engine.manualReviewService import ManualReviewService


def test_manual_review_required_for_removed_score_fields() -> None:
    """Forbidden score fields should force manual review."""
    review, reason = ManualReviewService().evaluate(["linkedin.lead_score"], {}, {}, {})

    assert review is True
    assert "Forbidden" in reason


def test_manual_review_required_for_personality_flag() -> None:
    """Personality analysis manual review flag should propagate."""
    review, reason = ManualReviewService().evaluate(
        [],
        {"manual_review_flag": True, "personality_analysis_reason": "Unsafe analysis blocked."},
        {},
        {},
    )

    assert review is True
    assert reason == "Unsafe analysis blocked."
