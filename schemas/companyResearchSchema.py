"""Stable schemas for company-level research output."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

INSUFFICIENT_DATA = "Insufficient data."

CompanyWebsiteStatus = Literal["valid", "invalid", "inferred", "missing"]
CompanyResearchSourceType = Literal[
    "official_website",
    "linkedin_company_page",
    "careers_page",
    "company_news",
    "search_result",
    "email_domain",
    "insufficient_data",
]
CompanyResearchStatus = Literal[
    "ready_for_personalization",
    "company_basic_data_found",
    "recent_news_found",
    "company_values_found",
    "company_fallback_used",
    "company_website_missing",
    "company_not_found",
    "insufficient_data",
    "manual_review_required",
    "company_research_failed",
]
LinkedInResearchStatus = Literal[
    "ready_for_personalization",
    "insufficient_data",
    "company_fallback_used",
    "linkedin_missing",
    "linkedin_invalid",
    "linkedin_inaccessible",
    "research_failed",
]


class StrictCompanyResearchModel(BaseModel):
    """Base model with deterministic serialization and strict fields."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ApprovedCompanySource(StrictCompanyResearchModel):
    """Approved company-level source snippet provided to the module."""

    source_type: CompanyResearchSourceType
    url: str = ""
    title: str = ""
    text: str = ""
    date_or_timeframe: str = INSUFFICIENT_DATA


class CompanyResearchInput(StrictCompanyResearchModel):
    """Input from cleaned records and prior LinkedIn research status."""

    campaign_id: str = ""
    prospect_id: str = ""
    company_name: str = ""
    company_website: str = ""
    company_linkedin_url: str = ""
    target_role: str = ""
    target_country: str = ""
    prospect_email: str = ""
    linkedin_research_status: LinkedInResearchStatus = "insufficient_data"
    enrichment_mode: bool = False
    approved_sources: list[ApprovedCompanySource] = Field(default_factory=list)


class CompanyRecentUpdate(StrictCompanyResearchModel):
    """Evidence-backed recent company update."""

    update: str
    evidence: str
    source_type: CompanyResearchSourceType
    date_or_timeframe: str = INSUFFICIENT_DATA


class CompanyResearchOutput(StrictCompanyResearchModel):
    """Deterministic JSON output for company-level personalization intelligence."""

    company_name_original: str = ""
    company_name_cleaned: str = ""
    company_website: str = ""
    company_website_status: CompanyWebsiteStatus = "missing"
    company_linkedin_url: str = ""
    company_research_status: CompanyResearchStatus = "insufficient_data"
    company_research_reason: str = INSUFFICIENT_DATA
    company_research_source_type: CompanyResearchSourceType = "insufficient_data"
    company_overview: str = INSUFFICIENT_DATA
    industry: str = INSUFFICIENT_DATA
    products_services_summary: str = INSUFFICIENT_DATA
    company_values_summary: str = INSUFFICIENT_DATA
    recent_company_updates: list[CompanyRecentUpdate] = Field(default_factory=list)
    growth_or_hiring_signal: str = INSUFFICIENT_DATA
    role_relevance_context: str = INSUFFICIENT_DATA
    country_relevance_context: str = INSUFFICIENT_DATA
    company_personalization_hooks: list[str] = Field(default_factory=lambda: [INSUFFICIENT_DATA])
    company_email_angle: str = INSUFFICIENT_DATA
    manual_review_flag: bool = False

    @field_validator("company_personalization_hooks")
    @classmethod
    def hooks_must_be_bounded(cls, value: list[str]) -> list[str]:
        """Ensure hooks are deterministic and bounded to one to three entries."""
        if not value:
            return [INSUFFICIENT_DATA]
        if len(value) > 3:
            raise ValueError("Company personalization hooks must contain at most three items.")
        return value
