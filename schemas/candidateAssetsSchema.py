"""Schemas for candidate assets and proof metadata."""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

INSUFFICIENT_PROOF = "Insufficient supporting proof."

ProofStatus = Literal[
    "proof_ready",
    "partial_proof_available",
    "insufficient_supporting_proof",
    "invalid_asset_link",
    "manual_review_required",
    "proof_processing_failed",
]
AssetType = Literal[
    "linkedin_profile",
    "resume",
    "intro_video",
    "portfolio",
    "project_case_study",
    "github",
    "presentation",
]
LinkedInProfileStatus = Literal["valid", "invalid", "missing"]
ResumeType = Literal["uploaded_metadata", "url", "cloud_document", "missing"]
VideoType = Literal["intro video", "portfolio demo", "project walkthrough", "case study"]


class StrictCandidateAssetsModel(BaseModel):
    """Strict deterministic base schema."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CandidateAssetInput(StrictCandidateAssetsModel):
    """Candidate-provided assets and proof settings."""

    campaign_id: str = ""
    candidate_id: str = ""
    resume_url: str = ""
    resume_metadata: dict = Field(default_factory=dict)
    linkedin_url: str = ""
    youtube_video_url: str = ""
    portfolio_links: list[str] = Field(default_factory=list)
    candidate_positioning: str = ""
    candidate_proof_points: list[str] = Field(default_factory=list)
    target_role: str = ""
    role_country_positioning: str = ""


class ResumeReference(StrictCandidateAssetsModel):
    """Safe resume reference metadata."""

    resume_available: bool = False
    resume_type: ResumeType = "missing"
    resume_reference_url: str = ""


class VideoAsset(StrictCandidateAssetsModel):
    """Normalized video asset metadata."""

    video_type: VideoType = "intro video"
    video_title: str = ""
    video_url: str = ""


class CandidateAssetsOutput(StrictCandidateAssetsModel):
    """Stable output for candidate asset proof metadata."""

    campaign_id: str = ""
    candidate_id: str = ""
    proof_status: ProofStatus = "insufficient_supporting_proof"
    proof_reason: str = INSUFFICIENT_PROOF
    linkedin_profile_url: str = ""
    linkedin_profile_status: LinkedInProfileStatus = "missing"
    resume_reference: ResumeReference = Field(default_factory=ResumeReference)
    video_assets: list[VideoAsset] = Field(default_factory=list)
    portfolio_assets: list[str] = Field(default_factory=list)
    professional_positioning_summary: str = INSUFFICIENT_PROOF
    why_relevant_summary: str = INSUFFICIENT_PROOF
    candidate_proof_snippets: list[str] = Field(default_factory=lambda: [INSUFFICIENT_PROOF])
    asset_types_detected: list[AssetType] = Field(default_factory=list)
    manual_review_flag: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
