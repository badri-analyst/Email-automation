"""Tests for decision status assignment and controller decisions."""

from orchestration.decisionEnginePipeline import DecisionEnginePipeline
from schemas.decisionSchema import DecisionOutput
from services.decision_engine.decisionStatusService import DecisionStatusService


def _base_payload() -> dict[str, object]:
    return {
        "campaign_id": "c1",
        "prospect_id": "p1",
        "cleaning_output": {
            "email": "jane@example.com",
            "full_name": "Jane Smith",
            "company_name": "Acme",
            "role_title": "Business Analyst",
            "validation_status": "valid",
        },
        "role_country_output": {
            "role_country_status": "ready_for_personalization",
            "normalized_role": "Business Analyst",
            "personalization_guidance": ["Use stakeholder alignment.", "Use measurable outcomes.", "Avoid generic claims."],
            "things_to_avoid": ["fake metrics"],
        },
        "linkedin_research_output": {"research_status": "ready_for_personalization", "personalization_insights": ["Mention process evidence."]},
        "company_research_output": {"company_research_status": "company_basic_data_found"},
        "personality_analysis_output": {"personality_analysis_status": "linkedin_profile_analysis_used"},
        "campaign_settings": {"smtp_configured": True, "smtp_valid": True, "sending_enabled": True},
    }


def test_decision_status_assignment_for_duplicate() -> None:
    """Duplicate rows should map to skip duplicate."""
    status, action, _ = DecisionStatusService().assign(False, "skipped_duplicate", "blocked", "skip", False)

    assert status == "skipped_duplicate"
    assert action == "skip_duplicate"


def test_decision_engine_blocks_invalid_email() -> None:
    """Invalid email rows should block sending."""
    payload = _base_payload()
    payload["cleaning_output"] = {"email": "bad", "validation_status": "invalid"}

    result = DecisionEnginePipeline().decide(payload)

    assert result.decision_status == "blocked_invalid_email"
    assert result.next_action == "skip_sending"


def test_decision_engine_skips_duplicate() -> None:
    """Confirmed duplicates should be skipped."""
    payload = _base_payload()
    payload["cleaning_output"]["is_duplicate"] = True

    result = DecisionEnginePipeline().decide(payload)

    assert result.decision_status == "skipped_duplicate"
    assert result.next_action == "skip_duplicate"


def test_decision_engine_ready_for_sending() -> None:
    """Ready context with SMTP should be allowed to send."""
    result = DecisionEnginePipeline().decide(_base_payload())

    assert result.decision_status == "ready_for_sending"
    assert result.email_send_permission == "allowed"
    assert result.final_personalization_payload.prospect["email"] == "jane@example.com"


def test_decision_engine_company_fallback() -> None:
    """Company fallback should be selected when LinkedIn is weak."""
    payload = _base_payload()
    payload["linkedin_research_output"] = {"research_status": "linkedin_inaccessible"}
    payload["personality_analysis_output"] = {}

    result = DecisionEnginePipeline().decide(payload)

    assert result.decision_status == "company_fallback_selected"
    assert result.selected_research_path == "company_fallback"
    assert result.fallback_used is True


def test_decision_engine_role_country_only() -> None:
    """Role-country-only fallback should be selected when research is weak."""
    payload = _base_payload()
    payload["linkedin_research_output"] = {"research_status": "insufficient_data"}
    payload["company_research_output"] = {"company_research_status": "insufficient_data"}
    payload["personality_analysis_output"] = {}

    result = DecisionEnginePipeline().decide(payload)

    assert result.decision_status == "role_country_only_selected"
    assert result.next_action == "run_role_country_only_personalization"


def test_decision_engine_manual_review_for_score_field() -> None:
    """Forbidden score fields should be removed and force manual review."""
    payload = _base_payload()
    payload["linkedin_research_output"]["lead_score"] = 10

    result = DecisionEnginePipeline().decide(payload)

    assert result.decision_status == "manual_review_required"
    assert result.manual_review_flag is True
    assert "lead_score" in result.manual_review_reason


def test_decision_engine_smtp_not_configured() -> None:
    """SMTP blocked state should prevent sending and allow draft generation."""
    payload = _base_payload()
    payload["campaign_settings"] = {"smtp_configured": False, "smtp_valid": False, "sending_enabled": True}

    result = DecisionEnginePipeline().decide(payload)

    assert result.decision_status == "smtp_not_configured"
    assert result.email_send_permission == "blocked"
    assert result.next_action == "generate_draft"


def test_decision_output_schema_rejects_scores() -> None:
    """Decision schema should reject extra scoring fields."""
    payload = DecisionOutput().model_dump()
    payload["decision_score"] = 1

    try:
        DecisionOutput.model_validate(payload)
    except Exception as exc:
        assert "Extra inputs are not permitted" in str(exc)
    else:
        raise AssertionError("Expected schema validation to reject score field.")


def test_campaign_summary_counts_decisions() -> None:
    """Pipeline should produce campaign-level summary counts."""
    pipeline = DecisionEnginePipeline()
    pipeline.decide(_base_payload())
    duplicate_payload = _base_payload()
    duplicate_payload["prospect_id"] = "p2"
    duplicate_payload["cleaning_output"]["is_duplicate"] = True
    pipeline.decide(duplicate_payload)

    summary = pipeline.summarize_campaign("c1")

    assert summary.ready_count == 1
    assert summary.skipped_count == 1
