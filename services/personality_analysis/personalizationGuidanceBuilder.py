"""Personalization guidance builder."""

from schemas.personalityAnalysisSchema import (
    CommunicationStyleOutput,
    INSUFFICIENT_DATA,
    ProfessionalBehavioralSignalOutput,
    ProfessionalMotivatorOutput,
)


class PersonalizationGuidanceBuilder:
    """Generate concise downstream personalization instructions."""

    def build(
        self,
        communication_style: CommunicationStyleOutput,
        signals: list[ProfessionalBehavioralSignalOutput],
        motivators: list[ProfessionalMotivatorOutput],
        role_country_context: str,
    ) -> list[str]:
        """Return three to five actionable personalization guidance points."""
        guidance: list[str] = []

        if communication_style.tone != "Insufficient data":
            guidance.append(f"Use {communication_style.tone.lower()} wording supported by professional evidence.")
        if communication_style.structure != "Insufficient data":
            guidance.append(f"Mirror a {communication_style.structure.lower()} structure without copying source text.")
        if signals:
            guidance.append(f"Connect the message to {signals[0].signal.lower()} professional work patterns.")
        if motivators:
            guidance.append(f"Emphasize {motivators[0].motivator.lower()} with a factual proof point.")
        if role_country_context:
            guidance.append("Apply role-country guidance for skills, tone, and proof-point selection.")

        return guidance[:5] if len(guidance) >= 3 else [INSUFFICIENT_DATA]
