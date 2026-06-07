"""Email personalization repository."""

from schemas.emailPersonalizationSchema import EmailPersonalizationOutput


class EmailPersonalizationRepository:
    """In-memory repository for generated drafts during campaign execution."""

    def __init__(self) -> None:
        self._store: dict[tuple[str, str], EmailPersonalizationOutput] = {}

    def save(self, output: EmailPersonalizationOutput) -> None:
        """Save generated draft metadata."""
        self._store[(output.campaign_id, output.prospect_id)] = output

    def get(self, campaign_id: str, prospect_id: str) -> EmailPersonalizationOutput | None:
        """Return stored generated draft."""
        return self._store.get((campaign_id, prospect_id))
