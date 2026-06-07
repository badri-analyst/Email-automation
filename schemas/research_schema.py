"""Stable JSON schemas for LinkedIn research output."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

INSUFFICIENT_DATA = "Insufficient data."

ResearchStatus = Literal[
    "ready_for_personalization",
    "insufficient_data",
    "company_fallback_used",
    "linkedin_missing",
    "linkedin_invalid",
    "linkedin_inaccessible",
    "research_failed",
]


class StrictResearchModel(BaseModel):
    """Base model with deterministic serialization behavior."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ResearchInput(StrictResearchModel):
    """Cleaned prospect record plus approved public research text."""

    full_name: str = ""
    role_title: str = ""
    company_name: str = ""
    normalized_company_name: str = ""
    linkedin_url: str = ""
    country: str = ""
    industry: str = ""
    profile_summary: str = ""
    bio: str = ""
    posts: list[str] = Field(default_factory=list)
    company_content: str = ""
    interviews: list[str] = Field(default_factory=list)
    company_updates: list[str] = Field(default_factory=list)
    linkedin_accessible: bool = True


class Overview(StrictResearchModel):
    """Factual prospect overview separated from inferred signals."""

    summary: str = INSUFFICIENT_DATA
    role: str = ""
    company: str = ""
    industry: str = INSUFFICIENT_DATA


class RecentUpdate(StrictResearchModel):
    """Evidence-backed company or professional update."""

    update: str = INSUFFICIENT_DATA
    evidence: str = INSUFFICIENT_DATA
    date_or_timeframe: str = INSUFFICIENT_DATA


class CommunicationStyle(StrictResearchModel):
    """Evidence-backed communication style signals."""

    tone: str = INSUFFICIENT_DATA
    structure: str = INSUFFICIENT_DATA
    energy: str = INSUFFICIENT_DATA
    audience_focus: str = INSUFFICIENT_DATA
    evidence: str = INSUFFICIENT_DATA


class ProfessionalBehavioralSignal(StrictResearchModel):
    """Allowed professional behavioral signal with evidence."""

    signal: str
    explanation: str
    evidence: str

    @field_validator("evidence")
    @classmethod
    def evidence_required(cls, value: str) -> str:
        """Require evidence or the explicit insufficient-data marker."""
        if not value:
            raise ValueError("Evidence is required.")
        return value


class ProfessionalMotivator(StrictResearchModel):
    """Allowed professional motivator with supporting evidence."""

    motivator: str
    why: str
    evidence: str

    @field_validator("evidence")
    @classmethod
    def evidence_required(cls, value: str) -> str:
        """Require evidence or the explicit insufficient-data marker."""
        if not value:
            raise ValueError("Evidence is required.")
        return value


class PersuasionProfile(StrictResearchModel):
    """Professional outreach messaging guidance."""

    best_messaging_style: str = INSUFFICIENT_DATA
    what_to_emphasize: str = INSUFFICIENT_DATA
    what_to_avoid: str = INSUFFICIENT_DATA


class LinkedInResearchOutput(StrictResearchModel):
    """Deterministic JSON output for email personalization."""

    overview: Overview = Field(default_factory=Overview)
    recent_news_or_updates: list[RecentUpdate] = Field(default_factory=lambda: [RecentUpdate()])
    communication_style: CommunicationStyle = Field(default_factory=CommunicationStyle)
    professional_behavioral_signals: list[ProfessionalBehavioralSignal] = Field(default_factory=list)
    professional_motivators: list[ProfessionalMotivator] = Field(default_factory=list)
    persuasion_profile: PersuasionProfile = Field(default_factory=PersuasionProfile)
    personalization_insights: list[str] = Field(default_factory=lambda: [INSUFFICIENT_DATA])
    research_status: ResearchStatus = "insufficient_data"
    research_reason: str = INSUFFICIENT_DATA
