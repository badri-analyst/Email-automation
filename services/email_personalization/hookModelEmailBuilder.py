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
        candidate = payload.get("candidate", {})
        link_lines = []
        if candidate.get("linkedin_url"):
            link_lines.append(f"LinkedIn: {candidate['linkedin_url']}")
        if candidate.get("resume_url"):
            link_lines.append(f"Resume: {candidate['resume_url']}")
        if candidate.get("youtube_url"):
            link_lines.append(f"Why Should You Hire Me: {candidate['youtube_url']}")
        if candidate.get("portfolio_url"):
            link_lines.append(f"Portfolio: {candidate['portfolio_url']}")
        links_block = "\n".join(link_lines)

        phone = candidate.get("phone", "")
        name = candidate.get("full_name", "")
        sign_off_parts = ["Regards,", name] + ([phone] if phone else [])
        sign_off = "\n".join(p for p in sign_off_parts if p)

        parts = [
            opening,
            self._positioning.build(payload),
            self._proof.build(payload),
            self._resume.build(),
            cta_sentence,
        ]
        if links_block:
            parts.append(links_block)
        parts.append(sign_off)
        body = "\n\n".join(parts)
        metadata = PersonalizationUsed(
            trigger=trigger,
            action=cta_sentence,
            variable_reward="A concise, relevant proof point or process improvement example.",
            investment="A quick look, short reply, or resume review.",
        )
        return body, cta_type, metadata, SourcesUsed(**source_flags)
