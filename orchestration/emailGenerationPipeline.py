"""Batch orchestration for email draft generation."""

from schemas.emailPersonalizationSchema import EmailPersonalizationInput, EmailPersonalizationOutput
from services.email_personalization.emailPersonalizationController import EmailPersonalizationController
from services.email_personalization.emailPersonalizationRepository import EmailPersonalizationRepository


class EmailGenerationPipeline:
    """Generate email drafts for campaign rows without sending them."""

    def __init__(self, repository: EmailPersonalizationRepository | None = None) -> None:
        self._repository = repository or EmailPersonalizationRepository()
        self._controller = EmailPersonalizationController(repository=self._repository)

    def generate(self, payload: EmailPersonalizationInput | dict[str, object]) -> EmailPersonalizationOutput:
        """Generate one email draft."""
        return self._controller.generate(payload)

    def generate_batch(self, payloads: list[EmailPersonalizationInput | dict[str, object]]) -> list[EmailPersonalizationOutput]:
        """Generate email drafts for a campaign batch."""
        return [self.generate(payload) for payload in payloads]
