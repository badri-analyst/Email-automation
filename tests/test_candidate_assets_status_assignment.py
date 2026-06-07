"""Tests for candidate proof status assignment."""

from services.candidate_assets.proofStatusService import ProofStatusService


def test_proof_status_ready_with_multiple_assets() -> None:
    """Multiple proof assets should be proof_ready."""
    status, reason = ProofStatusService().assign("valid", True, 1, 1, ["workflow example"], False, False)

    assert status == "proof_ready"
    assert reason


def test_proof_status_invalid_link() -> None:
    """Invalid asset links should produce invalid status."""
    status, _ = ProofStatusService().assign("invalid", False, 0, 0, ["workflow example"], True, False)

    assert status == "invalid_asset_link"


def test_candidate_assets_pipeline_outputs_structured_json() -> None:
    """Candidate assets pipeline should produce stable structured output."""
    from orchestration.candidateAssetsPipeline import CandidateAssetsPipeline

    result = CandidateAssetsPipeline().process(
        {
            "campaign_id": "c1",
            "candidate_id": "candidate-1",
            "linkedin_url": "linkedin.com/in/jane",
            "resume_url": "https://drive.google.com/resume",
            "youtube_video_url": "https://youtube.com/watch?v=abc",
            "portfolio_links": ["https://github.com/jane/project"],
            "candidate_positioning": "Business Analyst focused on workflow clarity.",
            "candidate_proof_points": ["requirements clarification example"],
        }
    )

    assert result.proof_status == "proof_ready"
    assert "linkedin_profile" in result.asset_types_detected
    assert "github" in result.asset_types_detected


def test_candidate_assets_schema_rejects_scores() -> None:
    """Candidate assets schema should reject scoring fields."""
    from schemas.candidateAssetsSchema import CandidateAssetsOutput

    payload = CandidateAssetsOutput().model_dump()
    payload["candidate_score"] = 1

    try:
        CandidateAssetsOutput.model_validate(payload)
    except Exception as exc:
        assert "Extra inputs are not permitted" in str(exc)
    else:
        raise AssertionError("Expected schema validation to reject score field.")
