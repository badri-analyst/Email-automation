"""Central deterministic decision engine controller."""

from typing import Any

from schemas.decisionSchema import CampaignDecisionSummary, DecisionInput, DecisionOutput
from services.decision_engine.decisionRepository import DecisionRepository
from services.decision_engine.finalPayloadBuilder import FinalPayloadBuilder
from utils.logger import get_logger

logger = get_logger(__name__)


class DecisionEngineController:
    """Three gate checks then build the final email payload."""

    def __init__(self, repository: DecisionRepository | None = None, max_attempts: int = 2) -> None:
        self._payload_builder = FinalPayloadBuilder()
        self._repository = repository or DecisionRepository()
        self._max_attempts = max(1, max_attempts)

    def decide(self, payload: DecisionInput | dict[str, Any]) -> DecisionOutput:
        """Run decision with failure isolation."""
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
                    )
        return DecisionOutput(decision_status="decision_failed", next_action="stop_processing")

    def summarize_campaign(self, campaign_id: str) -> CampaignDecisionSummary:
        """Return campaign-level decision summary counts."""
        summary = CampaignDecisionSummary()
        for output in self._repository.list_campaign(campaign_id):
            if output.decision_status == "ready_for_sending":
                summary.ready_count += 1
            elif output.decision_status == "skipped_duplicate":
                summary.skipped_count += 1
            elif output.decision_status in {"blocked_invalid_email", "gmail_not_configured", "decision_failed"}:
                summary.blocked_count += 1
        return summary

    def _decide_once(self, request: DecisionInput) -> DecisionOutput:
        """Three gate checks then build payload."""
        cleaning = request.cleaning_output
        settings = request.campaign_settings

        # Gate 1 — duplicate check
        duplicate = bool(cleaning.get("is_duplicate") or cleaning.get("Is Duplicate"))
        if duplicate:
            return DecisionOutput(
                campaign_id=request.campaign_id,
                prospect_id=request.prospect_id,
                decision_status="skipped_duplicate",
                decision_reason="Duplicate row skipped.",
                next_action="skip_duplicate",
                email_send_permission="blocked",
                email_send_block_reason="Duplicate.",
            )

        # Gate 2 — valid email check
        email = str(cleaning.get("email", cleaning.get("Email", ""))).strip()
        if not email:
            return DecisionOutput(
                campaign_id=request.campaign_id,
                prospect_id=request.prospect_id,
                decision_status="blocked_invalid_email",
                decision_reason="Email address is missing.",
                next_action="skip_sending",
                email_send_permission="blocked",
                email_send_block_reason="Email address is missing.",
            )

        # Gate 3 — Gmail connected check
        if not settings.gmail_configured or not settings.gmail_valid or not settings.sending_enabled:
            return DecisionOutput(
                campaign_id=request.campaign_id,
                prospect_id=request.prospect_id,
                decision_status="gmail_not_configured",
                decision_reason="Gmail is not connected.",
                next_action="stop_processing",
                email_send_permission="blocked",
                email_send_block_reason="Gmail OAuth2 is not configured or invalid.",
            )

        # All gates passed — build the email payload
        final_payload = self._payload_builder.build(
            cleaning=cleaning,
            role_country=request.role_country_output,
            linkedin=request.linkedin_research_output,
            company=request.company_research_output,
            candidate_profile=request.candidate_profile,
        )

        output = DecisionOutput(
            campaign_id=request.campaign_id,
            prospect_id=request.prospect_id,
            decision_status="ready_for_sending",
            decision_reason="All gates passed. Email payload ready.",
            next_action="send_email",
            email_send_permission="allowed",
            final_personalization_payload=final_payload,
        )
        self._repository.save(output)
        return output
