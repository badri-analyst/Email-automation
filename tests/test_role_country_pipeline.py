"""Tests for role-country intelligence pipeline."""

from orchestration.roleCountryPipeline import RoleCountryPipeline
from schemas.roleCountrySchema import RoleCountryOutput
from services.role_country.roleCountryRepository import RoleCountryRepository


def test_role_country_pipeline_generates_ready_output() -> None:
    """Supported role-country pairs should produce personalization-ready guidance."""
    result = RoleCountryPipeline().build_intelligence(
        {
            "campaign_id": "c1",
            "prospect_id": "p1",
            "target_role": "BA",
            "target_country": "USA",
            "candidate_positioning": "process improvement and stakeholder alignment",
        }
    )

    assert result.normalized_role == "Business Analyst"
    assert result.normalized_country == "United States"
    assert result.role_country_status == "ready_for_personalization"
    assert "Agile delivery" in result.country_role_expectations
    assert len(result.personalization_guidance) >= 3
    assert "score" not in result.model_dump_json().casefold()


def test_role_only_intelligence_when_country_missing() -> None:
    """Missing country should still use role-only intelligence."""
    result = RoleCountryPipeline().build_intelligence(
        {"campaign_id": "c1", "target_role": "Business Analyst"}
    )

    assert result.role_country_status == "role_only_intelligence_used"
    assert result.country_role_expectations == ["Insufficient data."]
    assert result.normalized_role == "Business Analyst"


def test_unsupported_role_country_handling() -> None:
    """Unsupported roles should not invent guidance."""
    result = RoleCountryPipeline().build_intelligence(
        {"campaign_id": "c1", "target_role": "Astronaut Wrangler", "target_country": "USA"}
    )

    assert result.role_country_status == "role_country_not_supported"
    assert result.role_summary == "Insufficient data."


def test_industry_refinement_is_applied() -> None:
    """Configured industry refinements should affect output and status."""
    result = RoleCountryPipeline().build_intelligence(
        {
            "campaign_id": "c1",
            "target_role": "BA",
            "target_country": "UK",
            "industry": "fintech",
        }
    )

    assert result.role_country_status == "industry_refinement_used"
    assert "regulatory workflows" in result.priority_skills


def test_seniority_refinement_is_applied() -> None:
    """Configured seniority refinements should affect output and status."""
    result = RoleCountryPipeline().build_intelligence(
        {
            "campaign_id": "c1",
            "target_role": "BA",
            "target_country": "USA",
            "seniority_level": "senior",
        }
    )

    assert result.role_country_status == "seniority_refinement_used"
    assert "strategic delivery" in result.priority_skills


def test_duplicate_cache_reuse_for_role_country_combinations() -> None:
    """Duplicate campaign role-country combinations should reuse cached output."""
    repository = RoleCountryRepository()
    pipeline = RoleCountryPipeline(repository=repository)
    payload = {
        "campaign_id": "campaign-1",
        "prospect_id": "p1",
        "target_role": "BA",
        "target_country": "USA",
    }

    first = pipeline.build_intelligence(payload)
    second = pipeline.build_intelligence({**payload, "prospect_id": "p2"})

    assert first == second


def test_role_country_json_schema_rejects_extra_fields() -> None:
    """Schema should reject score/ranking style extra fields."""
    payload = RoleCountryOutput().model_dump()
    payload["fit_score"] = 99

    try:
        RoleCountryOutput.model_validate(payload)
    except Exception as exc:
        assert "Extra inputs are not permitted" in str(exc)
    else:
        raise AssertionError("Expected schema validation to reject extra fields.")
