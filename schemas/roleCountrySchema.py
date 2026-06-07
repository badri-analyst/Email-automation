"""Pydantic schemas for role-country intelligence."""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

INSUFFICIENT_DATA = "Insufficient data."

RoleCountryStatus = Literal[
    "ready_for_personalization",
    "role_only_intelligence_used",
    "country_missing",
    "role_missing",
    "role_country_not_supported",
    "industry_refinement_used",
    "seniority_refinement_used",
    "insufficient_data",
    "manual_review_required",
    "role_country_research_failed",
]

IntelligenceSourceType = Literal[
    "configured_role_country_rule",
    "configured_role_rule",
    "configured_industry_refinement",
    "configured_seniority_refinement",
    "insufficient_data",
]


class StrictRoleCountryModel(BaseModel):
    """Strict deterministic base model."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class RoleCountryInput(StrictRoleCountryModel):
    """Input from upstream modules."""

    campaign_id: str = ""
    prospect_id: str = ""
    target_role: str = ""
    target_country: str = ""
    industry: str = ""
    seniority_level: str = ""
    candidate_positioning: str = ""


class RoleCountryOutput(StrictRoleCountryModel):
    """Stable JSON output for downstream personalization."""

    campaign_id: str = ""
    prospect_id: str = ""
    target_role: str = ""
    target_country: str = ""
    normalized_role: str = ""
    normalized_country: str = ""
    role_country_status: RoleCountryStatus = "insufficient_data"
    role_country_reason: str = INSUFFICIENT_DATA
    intelligence_source_type: IntelligenceSourceType = "insufficient_data"
    role_summary: str = INSUFFICIENT_DATA
    core_responsibilities: list[str] = Field(default_factory=lambda: [INSUFFICIENT_DATA])
    country_role_expectations: list[str] = Field(default_factory=lambda: [INSUFFICIENT_DATA])
    priority_skills: list[str] = Field(default_factory=lambda: [INSUFFICIENT_DATA])
    tools_or_frameworks: list[str] = Field(default_factory=lambda: [INSUFFICIENT_DATA])
    business_keywords: list[str] = Field(default_factory=lambda: [INSUFFICIENT_DATA])
    email_positioning_angle: str = INSUFFICIENT_DATA
    country_specific_email_tone: str = INSUFFICIENT_DATA
    proof_points_to_use: list[str] = Field(default_factory=lambda: [INSUFFICIENT_DATA])
    things_to_avoid: list[str] = Field(default_factory=lambda: [INSUFFICIENT_DATA])
    personalization_guidance: list[str] = Field(default_factory=lambda: [INSUFFICIENT_DATA])
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
