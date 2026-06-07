"""Schemas for professional communication and observable signal analysis."""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

INSUFFICIENT_DATA = "Insufficient data."

CommunicationTone = Literal[
    "Formal",
    "Casual",
    "Professional",
    "Friendly",
    "Authoritative",
    "Technical",
    "Direct",
    "Educational",
    "Neutral",
    "Insufficient data",
]
CommunicationStructure = Literal[
    "Short-form",
    "Storytelling",
    "Data-heavy",
    "Opinion-led",
    "Educational",
    "Practical",
    "Long-form",
    "Announcement-style",
    "Insufficient data",
]
CommunicationEnergy = Literal[
    "Calm",
    "Enthusiastic",
    "Assertive",
    "Neutral",
    "Persuasive",
    "Reflective",
    "High-energy",
    "Insufficient data",
]
PersonalityAnalysisStatus = Literal[
    "ready_for_personalization",
    "insufficient_data",
    "linkedin_profile_analysis_used",
    "linkedin_posts_analysis_used",
    "company_based_analysis_used",
    "manual_review_required",
    "personality_analysis_failed",
    "unsafe_analysis_blocked",
]
AnalysisSourceType = Literal[
    "linkedin_profile_summary",
    "linkedin_posts_summary",
    "company_research_summary",
    "role_country_intelligence",
    "combined_professional_context",
    "insufficient_data",
]


class StrictPersonalityModel(BaseModel):
    """Strict deterministic base model."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class PersonalityAnalysisInput(StrictPersonalityModel):
    """Input from upstream research and intelligence modules."""

    campaign_id: str = ""
    prospect_id: str = ""
    person_name: str = ""
    job_title: str = ""
    company_name: str = ""
    linkedin_profile_summary: str = ""
    linkedin_posts_summary: str = ""
    company_research_summary: str = ""
    role_country_intelligence: str = ""


class CommunicationStyleOutput(StrictPersonalityModel):
    """Observable professional communication style."""

    tone: CommunicationTone = "Insufficient data"
    structure: CommunicationStructure = "Insufficient data"
    energy: CommunicationEnergy = "Insufficient data"
    audience_focus: str = INSUFFICIENT_DATA
    evidence: str = INSUFFICIENT_DATA


class ProfessionalBehavioralSignalOutput(StrictPersonalityModel):
    """Evidence-backed professional behavioral signal."""

    signal: str
    explanation: str
    evidence: str

    @field_validator("evidence")
    @classmethod
    def evidence_required(cls, value: str) -> str:
        """Require evidence for every signal."""
        if not value:
            raise ValueError("Evidence is required.")
        return value


class ProfessionalMotivatorOutput(StrictPersonalityModel):
    """Evidence-backed professional motivator."""

    motivator: str
    why: str
    evidence: str

    @field_validator("evidence")
    @classmethod
    def evidence_required(cls, value: str) -> str:
        """Require evidence for every motivator."""
        if not value:
            raise ValueError("Evidence is required.")
        return value


class PersuasionProfileOutput(StrictPersonalityModel):
    """Safe professional messaging resonance guidance."""

    best_messaging_style: str = INSUFFICIENT_DATA
    what_to_emphasize: str = INSUFFICIENT_DATA
    what_to_avoid: str = INSUFFICIENT_DATA


class PersonalityAnalysisOutput(StrictPersonalityModel):
    """Stable JSON output for downstream email personalization."""

    campaign_id: str = ""
    prospect_id: str = ""
    person_name: str = ""
    job_title: str = ""
    company_name: str = ""
    personality_analysis_status: PersonalityAnalysisStatus = "insufficient_data"
    personality_analysis_reason: str = INSUFFICIENT_DATA
    analysis_source_type: AnalysisSourceType = "insufficient_data"
    communication_style: CommunicationStyleOutput = Field(default_factory=CommunicationStyleOutput)
    professional_behavioral_signals: list[ProfessionalBehavioralSignalOutput] = Field(default_factory=list)
    professional_motivators: list[ProfessionalMotivatorOutput] = Field(default_factory=list)
    persuasion_profile: PersuasionProfileOutput = Field(default_factory=PersuasionProfileOutput)
    personalization_guidance: list[str] = Field(default_factory=lambda: [INSUFFICIENT_DATA])
    manual_review_flag: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @field_validator("personalization_guidance")
    @classmethod
    def guidance_bounded(cls, value: list[str]) -> list[str]:
        """Ensure guidance is deterministic and bounded."""
        if not value:
            return [INSUFFICIENT_DATA]
        if value != [INSUFFICIENT_DATA] and not 3 <= len(value) <= 5:
            raise ValueError("Personalization guidance must contain three to five items.")
        return value
