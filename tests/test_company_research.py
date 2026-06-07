"""Tests for company research pipeline behavior."""

from orchestration.companyResearchPipeline import CompanyResearchPipeline
from schemas.companyResearchSchema import CompanyResearchOutput
from services.company_research.companyResearchRepository import CompanyResearchRepository
from services.company_research.companySourceSelector import CompanySourceSelector
from services.company_research.companyWebsiteService import CompanyWebsiteService


def test_company_website_validation_and_inference() -> None:
    """Website service should validate, infer, and reject unsafe domains."""
    service = CompanyWebsiteService()

    assert service.validate("acme.com") == ("https://acme.com", "valid")
    assert service.validate("linkedin.com") == ("linkedin.com", "invalid")
    assert service.validate("") == ("", "missing")
    assert service.infer_from_email_domain("jane@acme.io") == ("https://acme.io", "inferred")


def test_source_classification_prioritizes_official_sources() -> None:
    """Source selector should choose the strongest available source type."""
    selector = CompanySourceSelector()
    source = {
        "source_type": "company_news",
        "text": "Acme announced a product launch.",
    }

    from schemas.companyResearchSchema import ApprovedCompanySource

    assert selector.primary_source_type([ApprovedCompanySource.model_validate(source)], "valid") == "company_news"
    assert selector.primary_source_type([], "inferred") == "email_domain"


def test_company_research_handles_insufficient_data() -> None:
    """Weak company data should produce insufficient-data style output."""
    result = CompanyResearchPipeline().research_company(
        {
            "campaign_id": "c1",
            "prospect_id": "p1",
            "company_name": "",
            "linkedin_research_status": "insufficient_data",
        }
    )

    assert result.company_research_status in {"company_website_missing", "insufficient_data"}
    assert result.company_overview == "Insufficient data."
    assert result.company_personalization_hooks == ["Insufficient data."]


def test_company_research_generates_evidence_based_hooks() -> None:
    """Company research should generate safe hooks from approved evidence."""
    result = CompanyResearchPipeline().research_company(
        {
            "campaign_id": "c1",
            "prospect_id": "p1",
            "company_name": "ACME LLC",
            "company_website": "https://acme.com",
            "company_linkedin_url": "https://linkedin.com/company/acme",
            "target_role": "Business Analyst",
            "target_country": "India",
            "linkedin_research_status": "linkedin_inaccessible",
            "approved_sources": [
                {
                    "source_type": "official_website",
                    "url": "https://acme.com",
                    "text": "Acme is a SaaS platform offering workflow automation solutions for enterprise customers.",
                },
                {
                    "source_type": "careers_page",
                    "url": "https://acme.com/careers",
                    "text": "Acme values collaboration, customer value, and ownership while hiring analysts.",
                },
                {
                    "source_type": "company_news",
                    "url": "https://news.example/acme",
                    "text": "Acme announced a product launch in 2026 and is expanding hiring across operations.",
                },
            ],
        }
    )

    assert result.company_name_original == "ACME LLC"
    assert result.company_name_cleaned == "Acme"
    assert result.company_research_status == "recent_news_found"
    assert result.industry == "software"
    assert result.recent_company_updates
    assert result.company_personalization_hooks != ["Insufficient data."]
    assert "score" not in result.model_dump_json().casefold()


def test_company_research_duplicate_caching_reuses_results() -> None:
    """Campaign duplicate companies should reuse cached structured output."""
    repository = CompanyResearchRepository()
    pipeline = CompanyResearchPipeline(repository=repository)
    payload = {
        "campaign_id": "campaign-1",
        "prospect_id": "p1",
        "company_name": "Acme LLC",
        "company_website": "acme.com",
        "linkedin_research_status": "linkedin_missing",
        "approved_sources": [
            {
                "source_type": "official_website",
                "text": "Acme is a SaaS platform for customer workflow automation.",
            }
        ],
    }

    first = pipeline.research_company(payload)
    second = pipeline.research_company({**payload, "prospect_id": "p2", "company_website": "different.com"})

    assert first == second


def test_company_research_output_schema_validation() -> None:
    """Company research output should reject unstable extra fields."""
    payload = CompanyResearchOutput().model_dump()
    payload["lead_score"] = 1

    try:
        CompanyResearchOutput.model_validate(payload)
    except Exception as exc:
        assert "Extra inputs are not permitted" in str(exc)
    else:
        raise AssertionError("Expected schema validation to reject extra fields.")
