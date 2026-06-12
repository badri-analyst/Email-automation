"""Schemas for the deterministic decision engine."""

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

DecisionStatus = Literal[
    "ready_for_email_personalization",
    "ready_for_draft_generation",
    "ready_for_sending",
    "blocked_invalid_email",
    "skipped_duplicate",
    "company_fallback_selected",
    "role_country_only_selected",
    "manual_review_required",
    "insufficient_data",
    "gmail_not_configured",
    "decision_failed",
]
NextAction = Literal[
    "generate_email",
    "generate_draft",
    "send_email",
    "skip_sending",
    "skip_duplicate",
    "run_company_research",
    "run_role_country_only_personalization",
    "manual_review",
    "stop_processing",
]
EmailSendPermission = Literal["allowed", "draft_only", "blocked"]
SelectedResearchPath = Literal[
    "full_context",
    "linkedin_role_country",
    "company_fallback",
    "company_role_country",
    "role_country_only",
    "manual_review",
    "skip",
    "insufficient_data",
]
SelectedPersonalizationSource = Literal[
    "linkedin_research",
    "company_research",
    "role_country_intelligence",
    "personality_analysis",
    "combined_context",
    "none",
]


class StrictDecisionModel(BaseModel):
    """Strict deterministic base model."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CampaignSettings(StrictDecisionModel):
    """Campaign-level settings used for deterministic decisions."""

    gmail_configured: bool = False
    gmail_valid: bool = False
    sending_enabled: bool = False
    allow_draft_when_email_missing: bool = True
    require_manual_review_before_send: bool = True


class DecisionInput(StrictDecisionModel):
    """Structured upstream JSON payload for one prospect."""

    campaign_id: str = ""
    prospect_id: str = ""
    cleaning_output: dict[str, Any] = Field(default_factory=dict)
    role_country_output: dict[str, Any] = Field(default_factory=dict)
    linkedin_research_output: dict[str, Any] = Field(default_factory=dict)
    company_research_output: dict[str, Any] = Field(default_factory=dict)
    personality_analysis_output: dict[str, Any] = Field(default_factory=dict)
    campaign_settings: CampaignSettings = Field(default_factory=CampaignSettings)
    candidate_profile: dict[str, Any] = Field(default_factory=dict)


class FinalPersonalizationPayload(StrictDecisionModel):
    """Approved downstream personalization payload."""

    candidate: dict[str, Any] = Field(default_factory=dict)
    prospect: dict[str, Any] = Field(default_factory=dict)
    role_country_context: dict[str, Any] = Field(default_factory=dict)
    linkedin_context: dict[str, Any] = Field(default_factory=dict)
    company_context: dict[str, Any] = Field(default_factory=dict)
    personality_context: dict[str, Any] = Field(default_factory=dict)
    selected_hooks: list[str] = Field(default_factory=list)
    email_angle: str = ""
    things_to_avoid: list[str] = Field(default_factory=list)


class DecisionOutput(StrictDecisionModel):
    """Deterministic decision output for downstream personalization."""

    campaign_id: str = ""
    prospect_id: str = ""
    decision_status: DecisionStatus = "insufficient_data"
    decision_reason: str = "Insufficient data."
    next_action: NextAction = "manual_review"
    selected_research_path: SelectedResearchPath = "insufficient_data"
    selected_personalization_source: SelectedPersonalizationSource = "none"
    email_send_permission: EmailSendPermission = "blocked"
    email_send_block_reason: str = ""
    manual_review_flag: bool = False
    manual_review_reason: str = ""
    fallback_used: bool = False
    fallback_reason: str = ""
    final_personalization_payload: FinalPersonalizationPayload = Field(default_factory=FinalPersonalizationPayload)
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CampaignDecisionSummary(StrictDecisionModel):
    """Campaign-level decision summary."""

    ready_count: int = 0
    skipped_count: int = 0
    blocked_count: int = 0
    review_count: int = 0
    insufficient_data_count: int = 0
