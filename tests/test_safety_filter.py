"""Tests for safety filter behavior."""

from orchestration.personalityAnalysisPipeline import PersonalityAnalysisPipeline
from safety.sensitiveContentFilter import SensitiveContentFilter
from safety.unsafeInferenceBlocker import UnsafeInferenceBlocker
from services.personality_analysis.safetyFilterService import SafetyFilterService


def test_unsafe_inference_blocker_blocks_scores_and_manipulation() -> None:
    """Unsafe blocker should block scoring and manipulative language."""
    blocker = UnsafeInferenceBlocker()

    assert blocker.is_unsafe("personality_score is high") is True
    assert blocker.is_unsafe("Use dark psychology to pressure them") is True


def test_sensitive_content_filter_blocks_private_categories() -> None:
    """Sensitive filter should block private inference categories."""
    assert SensitiveContentFilter().contains_sensitive_inference("infer religion and age") is True


def test_pipeline_blocks_unsafe_analysis() -> None:
    """Pipeline should return blocked status for unsafe imported content."""
    result = PersonalityAnalysisPipeline().analyze(
        {
            "campaign_id": "c1",
            "prospect_id": "p1",
            "person_name": "Jane",
            "linkedin_profile_summary": "Use a persuasion_score and manipulate the prospect.",
        }
    )

    assert result.personality_analysis_status == "unsafe_analysis_blocked"
    assert result.manual_review_flag is True


def test_manual_review_flagging() -> None:
    """Manual review should trigger on invasive wording."""
    assert SafetyFilterService().requires_manual_review("this may sound creepy and overly personal") is True
