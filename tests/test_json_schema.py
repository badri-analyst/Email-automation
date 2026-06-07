"""Tests for deterministic LinkedIn research JSON schema validation."""

from schemas.research_schema import LinkedInResearchOutput
from services.linkedin_research.json_validator import ResearchJsonValidator


def test_research_output_has_stable_required_shape() -> None:
    """Default output should include the required deterministic JSON keys."""
    payload = LinkedInResearchOutput().model_dump()

    assert list(payload.keys()) == [
        "overview",
        "recent_news_or_updates",
        "communication_style",
        "professional_behavioral_signals",
        "professional_motivators",
        "persuasion_profile",
        "personalization_insights",
        "research_status",
        "research_reason",
    ]


def test_json_validator_rejects_extra_fields() -> None:
    """JSON validator should reject unstable extra fields."""
    payload = LinkedInResearchOutput().model_dump()
    payload["score"] = 98

    assert ResearchJsonValidator().is_valid(payload) is False


def test_json_validator_accepts_valid_schema() -> None:
    """JSON validator should accept the stable output schema."""
    payload = LinkedInResearchOutput().model_dump()

    assert ResearchJsonValidator().is_valid(payload) is True
