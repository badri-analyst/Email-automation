"""Tests for personality-safe communication analysis pipeline."""

from orchestration.personalityAnalysisPipeline import PersonalityAnalysisPipeline
from schemas.personalityAnalysisSchema import PersonalityAnalysisOutput
from services.personality_analysis.personalityAnalysisRepository import PersonalityAnalysisRepository


def test_pipeline_generates_linkedin_posts_analysis() -> None:
    """Pipeline should use LinkedIn posts evidence when available."""
    result = PersonalityAnalysisPipeline().analyze(
        {
            "campaign_id": "c1",
            "prospect_id": "p1",
            "person_name": "Jane Smith",
            "job_title": "Business Analyst",
            "company_name": "Acme",
            "linkedin_posts_summary": (
                "Excited to share a practical framework for stakeholder collaboration, "
                "workflow process improvement, and customer value."
            ),
            "role_country_intelligence": "Emphasize stakeholder alignment and measurable outcomes.",
        }
    )

    assert result.personality_analysis_status == "linkedin_posts_analysis_used"
    assert result.professional_behavioral_signals
    assert result.professional_motivators
    assert len(result.personalization_guidance) >= 3


def test_pipeline_uses_company_based_fallback_without_individual_inference() -> None:
    """Company context should be used as fallback when person content is weak."""
    result = PersonalityAnalysisPipeline().analyze(
        {
            "campaign_id": "c1",
            "prospect_id": "p1",
            "person_name": "Jane Smith",
            "company_name": "Acme",
            "company_research_summary": "Acme communicates customer value, collaboration, and process efficiency.",
        }
    )

    assert result.personality_analysis_status == "company_based_analysis_used"
    assert result.analysis_source_type == "company_research_summary"


def test_pipeline_insufficient_data_handling() -> None:
    """Weak inputs should not generate claims."""
    result = PersonalityAnalysisPipeline().analyze({"campaign_id": "c1", "person_name": "Jane"})

    assert result.personality_analysis_status == "insufficient_data"
    assert result.communication_style.evidence == "Insufficient data."
    assert result.personalization_guidance == ["Insufficient data."]


def test_pipeline_duplicate_cache_reuse() -> None:
    """Duplicate campaign/person analysis should reuse cached output."""
    repository = PersonalityAnalysisRepository()
    pipeline = PersonalityAnalysisPipeline(repository=repository)
    payload = {
        "campaign_id": "campaign-1",
        "prospect_id": "p1",
        "person_name": "Jane Smith",
        "job_title": "Business Analyst",
        "company_name": "Acme",
        "linkedin_profile_summary": "Jane shares practical workflow process improvement ideas for customers.",
    }

    first = pipeline.analyze(payload)
    second = pipeline.analyze({**payload, "prospect_id": "p2"})

    assert first == second


def test_personality_analysis_json_schema_rejects_scores() -> None:
    """Schema should reject hidden score fields."""
    payload = PersonalityAnalysisOutput().model_dump()
    payload["personality_score"] = 10

    try:
        PersonalityAnalysisOutput.model_validate(payload)
    except Exception as exc:
        assert "Extra inputs are not permitted" in str(exc)
    else:
        raise AssertionError("Expected schema validation to reject extra fields.")
