"""Tests for company research status assignment."""

from services.company_research.companyResearchStatusService import CompanyResearchStatusService


def test_company_status_assignment_for_recent_news() -> None:
    """Recent updates should produce recent-news status."""
    from schemas.companyResearchSchema import CompanyRecentUpdate

    update = CompanyRecentUpdate(
        update="Acme announced a launch.",
        evidence="Acme announced a launch.",
        source_type="company_news",
    )

    status, reason = CompanyResearchStatusService().assign(
        website_status="valid",
        overview="Acme builds software.",
        values_summary="Insufficient data.",
        updates=[update],
        growth_signal="Insufficient data.",
        linkedin_research_status="linkedin_missing",
        manual_review_flag=False,
    )

    assert status == "recent_news_found"
    assert reason


def test_company_status_assignment_for_manual_review() -> None:
    """Invalid websites should be able to route to manual review."""
    status, _ = CompanyResearchStatusService().assign(
        website_status="invalid",
        overview="Insufficient data.",
        values_summary="Insufficient data.",
        updates=[],
        growth_signal="Insufficient data.",
        linkedin_research_status="linkedin_missing",
        manual_review_flag=True,
    )

    assert status == "manual_review_required"
