"""Batch orchestration for the central decision engine."""

from schemas.decisionSchema import CampaignDecisionSummary, DecisionInput, DecisionOutput
from services.decision_engine.decisionEngineController import DecisionEngineController
from services.decision_engine.decisionRepository import DecisionRepository


class DecisionEnginePipeline:
    """Campaign decision pipeline with row-level failure isolation."""

    def __init__(self, repository: DecisionRepository | None = None) -> None:
        self._repository = repository or DecisionRepository()
        self._controller = DecisionEngineController(repository=self._repository)

    def decide(self, payload: DecisionInput | dict[str, object]) -> DecisionOutput:
        """Run decision for one row."""
        return self._controller.decide(payload)

    def decide_batch(self, payloads: list[DecisionInput | dict[str, object]]) -> list[DecisionOutput]:
        """Run decisions for a campaign batch."""
        return [self.decide(payload) for payload in payloads]

    def summarize_campaign(self, campaign_id: str) -> CampaignDecisionSummary:
        """Return campaign-level decision summary."""
        return self._controller.summarize_campaign(campaign_id)
