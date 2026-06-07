"""Tests for email length validation."""

from orchestration.emailGenerationPipeline import EmailGenerationPipeline
from services.email_personalization.emailQualityValidator import EmailQualityValidator


def _payload() -> dict[str, object]:
    return {
        "campaign_id": "c1",
        "prospect_id": "p1",
        "final_personalization_payload": {
            "prospect": {"first_name": "Jane", "email": "jane@example.com", "company": "Acme", "role": "Business Analyst"},
            "role_country_context": {
                "normalized_role": "Business Analyst",
                "business_keywords": ["workflow clarity"],
                "proof_points_to_use": ["workflow improvement example"],
                "email_positioning_angle": "Position around stakeholder alignment.",
            },
            "company_context": {"company_overview": "Acme builds workflow software."},
            "selected_hooks": ["Acme builds workflow software for enterprise teams. Evidence: approved source."],
            "personality_context": {"communication_style": {"tone": "Professional"}},
        },
    }


def test_email_body_under_130_words() -> None:
    """Generated body should stay under default word limit."""
    result = EmailGenerationPipeline().generate(_payload())

    assert result.word_count <= 130
    assert result.email_generation_status == "email_ready"


def test_quality_validator_detects_long_body() -> None:
    """Quality validator should reject long bodies."""
    ok, reason = EmailQualityValidator().validate("Short subject", "word " * 131)

    assert ok is False
    assert "body" in reason
