"""Tests for decision research path selection."""

from services.decision_engine.researchPathSelector import ResearchPathSelector


def test_research_path_full_context_priority() -> None:
    """Full context should be selected when all upstream modules are ready."""
    path, source, _ = ResearchPathSelector().select(
        {"role_country_status": "ready_for_personalization"},
        {"research_status": "ready_for_personalization"},
        {"company_research_status": "recent_news_found"},
        {"personality_analysis_status": "linkedin_posts_analysis_used"},
    )

    assert path == "full_context"
    assert source == "combined_context"


def test_research_path_company_role_country_fallback_candidate() -> None:
    """Company plus role-country should be selected when LinkedIn is weak."""
    path, source, _ = ResearchPathSelector().select(
        {"role_country_status": "ready_for_personalization"},
        {"research_status": "linkedin_inaccessible"},
        {"company_research_status": "company_basic_data_found"},
        {},
    )

    assert path == "company_role_country"
    assert source == "company_research"


def test_research_path_role_country_only() -> None:
    """Role-country-only should be selected when other sources are weak."""
    path, source, _ = ResearchPathSelector().select(
        {"role_country_status": "role_only_intelligence_used"},
        {"research_status": "insufficient_data"},
        {"company_research_status": "insufficient_data"},
        {},
    )

    assert path == "role_country_only"
    assert source == "role_country_intelligence"
