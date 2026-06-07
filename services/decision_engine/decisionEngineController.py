"""Central deterministic decision engine controller."""

from typing import Any

from schemas.decisionSchema import CampaignDecisionSummary, DecisionInput, DecisionOutput
from services.decision_engine.decisionRepository import DecisionRepository
from services.decision_engine.decisionStatusService import DecisionStatusService
from services.decision_engine.fallbackDecisionService import FallbackDecisionService
from services.decision_engine.finalPayloadBuilder import FinalPayloadBuilder
from services.decision_engine.manualReviewService import ManualReviewService
from services.decision_engine.researchPathSelector import ResearchPathSelector
from services.decision_engine.rowEligibilityService import RowEligibilityService
from services.decision_engine.scoreFieldGuardService import ScoreFieldGuardService
from services.decision_engine.sendPermissionService import SendPermissionService
from utils.logger import get_logger

logger = get_logger(__name__)


class DecisionEngineController:
    """Evaluate workflow readiness, safety, fallback, and downstream payload selection."""

    def __init__(self, repository: DecisionRepository | None = None, max_attempts: int = 2) -> None:
        self._score_guard = ScoreFieldGuardService()
        self._eligibility = RowEligibilityService()
        self._send_permission = SendPermissionService()
        self._path_selector = ResearchPathSelector()
        self._fallback = FallbackDecisionService()
        self._manual_review = ManualReviewService()
        self._payload_builder = FinalPayloadBuilder()
        self._status = DecisionStatusService()
        self._repository = repository or DecisionRepository()
        self._max_attempts = max(1, max_attempts)

    def decide(self, payload: DecisionInput | dict[str, Any]) -> DecisionOutput:
        """Run one deterministic decision with failure isolation."""
        for attempt in range(1, self._max_attempts + 1):
            try:
                request = payload if isinstance(payload, DecisionInput) else DecisionInput.model_validate(payload)
                return self._decide_once(request)
            except Exception as exc:
                logger.exception("Decision engine attempt %s failed", attempt)
                if attempt == self._max_attempts:
                    return DecisionOutput(
                        decision_status="decision_failed",
                        decision_reason=str(exc) or "Decision failed.",
                        next_action="stop_processing",
                        manual_review_flag=True,
                    )
        return DecisionOutput(decision_status="decision_failed", next_action="stop_processing", manual_review_flag=True)

    def summarize_campaign(self, campaign_id: str) -> CampaignDecisionSummary:
        """Return campaign-level decision summary counts."""
        summary = CampaignDecisionSummary()
        for output in self._repository.list_campaign(campaign_id):
            if output.decision_status in {"ready_for_email_personalization", "ready_for_draft_generation", "ready_for_sending"}:
                summary.ready_count += 1
            elif output.decision_status == "skipped_duplicate":
                summary.skipped_count += 1
            elif output.decision_status in {"blocked_invalid_email", "smtp_not_configured", "decision_failed"}:
                summary.blocked_count += 1
            elif output.decision_status == "manual_review_required":
                summary.review_count += 1
            elif output.decision_status == "insufficient_data":
                summary.insufficient_data_count += 1
        return summary

    def _decide_once(self, request: DecisionInput) -> DecisionOutput:
        """Run one decision pass."""
        raw_sections = {
            "cleaning_output": request.cleaning_output,
            "role_country_output": request.role_country_output,
            "linkedin_research_output": request.linkedin_research_output,
            "company_research_output": request.company_research_output,
            "personality_analysis_output": request.personality_analysis_output,
        }
        sanitized_sections, removed_fields = self._sanitize_sections(raw_sections)
        cleaning = sanitized_sections["cleaning_output"]
        role_country = sanitized_sections["role_country_output"]
        linkedin = sanitized_sections["linkedin_research_output"]
        company = sanitized_sections["company_research_output"]
        personality = sanitized_sections["personality_analysis_output"]

        eligible, eligibility_status, eligibility_reason = self._eligibility.evaluate(cleaning)
        email_present = bool(str(cleaning.get("email", cleaning.get("Email", ""))).strip())
        send_permission, send_block_reason = self._send_permission.evaluate(email_present, request.campaign_settings)
        selected_path, selected_source, path_reason = self._path_selector.select(role_country, linkedin, company, personality)
        fallback_used, fallback_path, fallback_reason = self._fallback.evaluate(selected_path, linkedin)
        manual_review, manual_review_reason = self._manual_review.evaluate(removed_fields, personality, company, role_country)
        effective_path = fallback_path if fallback_used else selected_path
        decision_status, next_action, status_reason = self._status.assign(
            eligible=eligible,
            eligibility_status=eligibility_status,
            send_permission=send_permission,
            selected_path=effective_path,
            manual_review=manual_review,
        )
        final_payload = self._payload_builder.build(cleaning, role_country, linkedin, company, personality, effective_path)
        reason = eligibility_reason or manual_review_reason or fallback_reason or status_reason or path_reason

        output = DecisionOutput(
            campaign_id=request.campaign_id,
            prospect_id=request.prospect_id,
            decision_status=decision_status,
            decision_reason=reason,
            next_action=next_action,
            selected_research_path=effective_path,
            selected_personalization_source=selected_source,
            email_send_permission=send_permission,
            email_send_block_reason=send_block_reason,
            manual_review_flag=manual_review,
            manual_review_reason=manual_review_reason,
            fallback_used=fallback_used,
            fallback_reason=fallback_reason,
            final_personalization_payload=final_payload,
        )
        self._repository.save(output)
        return output

    def _sanitize_sections(self, sections: dict[str, dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], list[str]]:
        """Sanitize all upstream sections and collect forbidden fields."""
        sanitized: dict[str, dict[str, Any]] = {}
        removed: list[str] = []
        for name, section in sections.items():
            clean_section, removed_fields = self._score_guard.sanitize(section)
            sanitized[name] = clean_section
            removed.extend([f"{name}.{field}" for field in removed_fields])
        return sanitized, removed
