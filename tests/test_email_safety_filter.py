"""Tests for email safety filtering."""

from orchestration.emailGenerationPipeline import EmailGenerationPipeline
from services.email_personalization.emailSafetyFilter import EmailSafetyFilter


def test_email_safety_filter_blocks_hallucination_risk() -> None:
    """Safety filter should block fake company fact language."""
    safe, reason = EmailSafetyFilter().check("Hello", "I saw your funding and wanted to reach out.")

    assert safe is False
    assert "funding" in reason


def test_email_pipeline_blocks_unsafe_content_from_payload() -> None:
    """Pipeline should block unsafe generated content."""
    result = EmailGenerationPipeline().generate(
        {
            "campaign_id": "c1",
            "prospect_id": "p1",
            "final_personalization_payload": {
                "prospect": {"company": "Acme", "role": "Business Analyst"},
                "selected_hooks": ["I saw your funding. Evidence: unsupported."],
            },
        }
    )

    assert result.email_generation_status == "blocked_unsafe_content"
    assert result.manual_review_flag is True
