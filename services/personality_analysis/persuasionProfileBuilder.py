"""Safe professional persuasion profile builder."""

from schemas.personalityAnalysisSchema import (
    CommunicationStyleOutput,
    INSUFFICIENT_DATA,
    PersuasionProfileOutput,
    ProfessionalMotivatorOutput,
)


class PersuasionProfileBuilder:
    """Build non-manipulative professional messaging guidance."""

    def build(
        self,
        communication_style: CommunicationStyleOutput,
        motivators: list[ProfessionalMotivatorOutput],
        role_country_context: str,
    ) -> PersuasionProfileOutput:
        """Return safe messaging guidance."""
        if communication_style.evidence == INSUFFICIENT_DATA and not motivators and not role_country_context:
            return PersuasionProfileOutput()

        style = "concise, professional, evidence-based messaging"
        if communication_style.tone != "Insufficient data":
            style = f"concise, {communication_style.tone.lower()}, evidence-based messaging"

        emphasis_items = [motivator.motivator for motivator in motivators[:3]]
        if role_country_context:
            emphasis_items.append("role-country positioning guidance")

        return PersuasionProfileOutput(
            best_messaging_style=style,
            what_to_emphasize=", ".join(emphasis_items) if emphasis_items else INSUFFICIENT_DATA,
            what_to_avoid="unsupported praise, personal assumptions, pressure tactics, overly familiar comments, or fake metrics",
        )
