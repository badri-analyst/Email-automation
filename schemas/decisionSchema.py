"""Schemas for the deterministic decision engine."""

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

DecisionStatus = Literal[
    "ready_for_sending",
    "blocked_invalid_email",
    "skipped_duplicate",
    "gmail_not_configured",
    "decision_failed",
]
NextAction = Literal[
    "send_email",
    "skip_sending",
    "skip_duplicate",
    "stop_processing",
]
EmailSendPermission = Literal["allowed", "blocked"]


class StrictDecisionModel(BaseModel):
    """Strict deterministic base model."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CampaignSettings(StrictDecisionModel):
    """Campaign-level settings used for deterministic decisions."""

    gmail_configured: bool = False
    gmail_valid: bool = False
    sending_enabled: bool = False


class DecisionInput(StrictDecisionModel):
    """Structured upstream JSON payload for one prospect."""

    campaign_id: str = ""
    prospect_id: str = ""
    cleaning_output: dict[str, Any] = Field(default_factory=dict)
    role_country_output: dict[str, Any] = Field(default_factory=dict)
    linkedin_research_output: dict[str, Any] = Field(default_factory=dict)
    company_research_output: dict[str, Any] = Field(default_factory=dict)
    campaign_settings: CampaignSettings = Field(default_factory=CampaignSettings)
    candidate_profile: dict[str, Any] = Field(default_factory=dict)


class FinalPersonalizationPayload(StrictDecisionModel):
    """Approved downstream personalization payload for email generation."""

    opening_hook: str = ""
    candidate: dict[str, Any] = Field(default_factory=dict)
    prospect: dict[str, Any] = Field(default_factory=dict)
    key_skills: list[str] = Field(default_factory=list)
    tone_guidance: str = ""
    company_context: dict[str, Any] = Field(default_factory=dict)
    api_key: str = ""
    backup_api_key: str = ""
    base_url: str = ""
    model: str = ""


class DecisionOutput(StrictDecisionModel):
    """Deterministic decision output for downstream personalization."""

    campaign_id: str = ""
    prospect_id: str = ""
    decision_status: DecisionStatus = "decision_failed"
    decision_reason: str = "Decision failed."
    next_action: NextAction = "stop_processing"
    email_send_permission: EmailSendPermission = "blocked"
    email_send_block_reason: str = ""
    final_personalization_payload: FinalPersonalizationPayload = Field(default_factory=FinalPersonalizationPayload)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CampaignDecisionSummary(StrictDecisionModel):
    """Campaign-level decision summary."""

    ready_count: int = 0
    skipped_count: int = 0
    blocked_count: int = 0
