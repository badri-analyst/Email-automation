"""Tests for fallback email generation."""

from orchestration.emailGenerationPipeline import EmailGenerationPipeline


def test_fallback_email_created_when_personalization_is_weak() -> None:
    """Weak payloads should create role-based fallback emails."""
    result = EmailGenerationPipeline().generate(
        {
            "campaign_id": "c1",
            "prospect_id": "p1",
            "final_personalization_payload": {
                "prospect": {"role": "Business Analyst", "company": "Acme"},
                "role_country_context": {"normalized_role": "Business Analyst"},
            },
        }
    )

    assert result.email_generation_status == "fallback_email_created"
    assert result.sources_used.fallback_used is True
    assert "I attached my resume" in result.email_body


def test_email_schema_rejects_score_fields() -> None:
    """Email schema should reject hidden scoring fields."""
    from schemas.emailPersonalizationSchema import EmailPersonalizationOutput

    payload = EmailPersonalizationOutput().model_dump()
    payload["email_score"] = 10

    try:
        EmailPersonalizationOutput.model_validate(payload)
    except Exception as exc:
        assert "Extra inputs are not permitted" in str(exc)
    else:
        raise AssertionError("Expected schema validation to reject score field.")
