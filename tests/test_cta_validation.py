"""Tests for CTA building and validation."""

from services.email_personalization.ctaBuilder import CtaBuilder


def test_cta_builder_returns_one_allowed_cta() -> None:
    """CTA builder should return one low-friction CTA."""
    cta_type, cta = CtaBuilder().build("recruiter")

    assert cta_type == "resume review"
    assert cta.count("?") == 1


def test_cta_validator_rejects_multiple_questions() -> None:
    """CTA validator should reject multiple asks."""
    assert CtaBuilder().is_valid_single_cta("Can we talk? Can you review?") is False
