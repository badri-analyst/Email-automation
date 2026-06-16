"""Schemas for deterministic email personalization."""

from datetime import datetime, timezone
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

EmailGenerationStatus = Literal[
    "email_ready",
    "draft_ready",
    "fallback_email_created",
    "manual_review_required",
    "insufficient_data",
    "blocked_invalid_payload",
    "blocked_unsafe_content",
    "email_generation_failed",
]
SubjectType = str  # open string — new subject types must not break validation
CtaType = Literal["quick look", "short reply", "resume review", "fit check", "permission to send ideas"]


class StrictEmailModel(BaseModel):
    """Strict deterministic base model."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class EmailPersonalizationInput(StrictEmailModel):
    """Input from the Decision Engine."""

    campaign_id: str = ""
    prospect_id: str = ""
    final_personalization_payload: dict = Field(default_factory=dict)
    variant: str = "recruiter"
    api_key: str = ""
    backup_api_key: str = ""
    base_url: str = ""
    model: str = ""


class PersonalizationUsed(StrictEmailModel):
    """Ethical Hook Model metadata."""

    trigger: str = ""
    action: str = ""
    variable_reward: str = ""
    investment: str = ""


class SourcesUsed(StrictEmailModel):
    """Source flags used during draft construction."""

    linkedin_context_used: bool = False
    company_context_used: bool = False
    role_country_context_used: bool = False
    personality_guidance_used: bool = False
    fallback_used: bool = False


class EmailPersonalizationOutput(StrictEmailModel):
    """Stable output for recruiter-facing email drafts."""

    campaign_id: str = ""
    prospect_id: str = ""
    subject_line: str = ""
    subject_type: SubjectType = "fallback"
    email_body: str = ""
    email_generation_status: EmailGenerationStatus = "insufficient_data"
    email_generation_reason: str = "Insufficient data."
    personalization_used: PersonalizationUsed = Field(default_factory=PersonalizationUsed)
    sources_used: SourcesUsed = Field(default_factory=SourcesUsed)
    cta_type: CtaType = "resume review"
    tone_used: str = "professional"
    word_count: int = 0
    manual_review_flag: bool = False
    manual_review_reason: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
