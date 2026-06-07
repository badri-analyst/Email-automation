"""Ethical Hook Model email assembly."""

from schemas.emailPersonalizationSchema import PersonalizationUsed, SourcesUsed
from services.email_personalization.candidatePositioningService import CandidatePositioningService
from services.email_personalization.candidateProofPointService import CandidateProofPointService
from services.email_personalization.ctaBuilder import CtaBuilder
from services.email_personalization.openingTriggerSelector import OpeningTriggerSelector
from services.email_personalization.resumeMentionBuilder import ResumeMentionBuilder


class HookModelEmailBuilder:
    """Assemble recruiter-ready email using safe Hook Model metadata."""

    def __init__(self) -> None:
        self._opening = OpeningTriggerSelector()
        self._positioning = CandidatePositioningService()
        self._proof = CandidateProofPointService()
        self._resume = ResumeMentionBuilder()
        self._cta = CtaBuilder()

    def build(self, payload: dict, variant: str) -> tuple[str, str, PersonalizationUsed, SourcesUsed]:
        """Return email body, CTA type, metadata, and sources used."""
        opening, trigger, source_flags = self._opening.select(payload)
        cta_type, cta_sentence = self._cta.build(variant)
        body = "\n\n".join(
            [
                opening,
                self._positioning.build(payload),
                self._proof.build(payload),
                self._resume.build(),
                cta_sentence,
            ]
        )
        metadata = PersonalizationUsed(
            trigger=trigger,
            action=cta_sentence,
            variable_reward="A concise, relevant proof point or process improvement example.",
            investment="A quick look, short reply, or resume review.",
        )
        return body, cta_type, metadata, SourcesUsed(**source_flags)
