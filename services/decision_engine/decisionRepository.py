"""Decision engine repository."""

from schemas.decisionSchema import DecisionOutput


class DecisionRepository:
    """In-memory repository for auditable decisions during a campaign run."""

    def __init__(self) -> None:
        self._store: dict[tuple[str, str], DecisionOutput] = {}

    def save(self, output: DecisionOutput) -> None:
        """Save decision output."""
        self._store[(output.campaign_id, output.prospect_id)] = output

    def list_campaign(self, campaign_id: str) -> list[DecisionOutput]:
        """Return decisions for a campaign."""
        return [output for (stored_campaign_id, _), output in self._store.items() if stored_campaign_id == campaign_id]
