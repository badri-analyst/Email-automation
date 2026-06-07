"""Tests for forbidden score/rating/ranking field guard."""

from services.decision_engine.scoreFieldGuardService import ScoreFieldGuardService


def test_score_field_guard_removes_forbidden_fields_recursively() -> None:
    """Score-like fields should be removed recursively and reported."""
    payload = {
        "lead_score": 99,
        "nested": {"fit_value": "high", "safe": "ok"},
        "items": [{"quality_rating": "A", "name": "Jane"}],
    }

    sanitized, removed = ScoreFieldGuardService().sanitize(payload)

    assert "lead_score" not in sanitized
    assert "fit_value" not in sanitized["nested"]
    assert "quality_rating" not in sanitized["items"][0]
    assert len(removed) == 3
