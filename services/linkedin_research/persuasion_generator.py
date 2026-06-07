"""Professional outreach guidance generation."""

from schemas.research_schema import INSUFFICIENT_DATA, PersuasionProfile, ProfessionalMotivator


class PersuasionGenerator:
    """Generate ethical professional messaging guidance from supported signals."""

    def generate(
        self,
        communication_tone: str,
        motivators: list[ProfessionalMotivator],
        has_company_fallback: bool,
    ) -> PersuasionProfile:
        """Return non-manipulative outreach guidance."""
        if communication_tone == INSUFFICIENT_DATA and not motivators and not has_company_fallback:
            return PersuasionProfile()

        motivator_names = [motivator.motivator for motivator in motivators]
        emphasis = ", ".join(motivator_names[:3]) if motivator_names else "public company context"
        style = "concise, evidence-led professional messaging"
        if communication_tone != INSUFFICIENT_DATA:
            style = f"concise, {communication_tone} professional messaging"

        return PersuasionProfile(
            best_messaging_style=style,
            what_to_emphasize=emphasis,
            what_to_avoid="unsupported claims, personal assumptions, pressure tactics, or unverifiable flattery",
        )
