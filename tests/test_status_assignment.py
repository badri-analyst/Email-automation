"""Tests for LinkedIn research status assignment."""

from schemas.research_schema import ResearchInput
from services.linkedin_research.status_manager import ResearchStatusManager


def test_status_assignment_handles_missing_linkedin_url() -> None:
    """Missing LinkedIn URL should be terminally classified."""
    status, reason = ResearchStatusManager().assign(ResearchInput(), "", "")

    assert status == "linkedin_missing"
    assert reason


def test_status_assignment_handles_invalid_linkedin_url() -> None:
    """Non-public-profile LinkedIn URL should be invalid."""
    payload = ResearchInput(linkedin_url="https://example.com/in/jane")

    status, _ = ResearchStatusManager().assign(payload, "profile evidence", "")

    assert status == "linkedin_invalid"


def test_status_assignment_uses_company_fallback_when_person_data_is_weak() -> None:
    """Company evidence should produce a company fallback status."""
    payload = ResearchInput(linkedin_url="https://linkedin.com/in/jane")

    status, reason = ResearchStatusManager().assign(payload, "", "Company announced a product launch.")

    assert status == "company_fallback_used"
    assert "company evidence" in reason.casefold()


def test_status_assignment_ready_when_person_evidence_exists() -> None:
    """Person evidence should produce ready-for-personalization status."""
    payload = ResearchInput(linkedin_url="https://linkedin.com/in/jane")

    status, _ = ResearchStatusManager().assign(payload, "Jane writes about data engineering.", "")

    assert status == "ready_for_personalization"
