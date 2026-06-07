"""Actionable personalization insight generation."""

from schemas.research_schema import (
    INSUFFICIENT_DATA,
    CommunicationStyle,
    ProfessionalMotivator,
    RecentUpdate,
)


class InsightGenerator:
    """Generate concise evidence-based personalization insights."""

    def generate(
        self,
        role: str,
        company: str,
        communication_style: CommunicationStyle,
        motivators: list[ProfessionalMotivator],
        updates: list[RecentUpdate],
    ) -> list[str]:
        """Return three to five practical insights when evidence supports them."""
        insights: list[str] = []

        for update in updates:
            if update.update != INSUFFICIENT_DATA:
                insights.append(f"Reference the public update: {update.update} Evidence: {update.evidence}")
                break

        if communication_style.tone != INSUFFICIENT_DATA:
            insights.append(
                f"Use {communication_style.tone} messaging and keep the note concise. "
                f"Evidence: {communication_style.evidence}"
            )

        for motivator in motivators[:2]:
            insights.append(f"Emphasize {motivator.motivator}: {motivator.why} Evidence: {motivator.evidence}")

        if role and company and insights:
            insights.append(f"Connect the outreach to {role} responsibilities at {company}. Evidence: cleaned record.")

        deduped = list(dict.fromkeys(insights))
        return deduped[:5] if deduped else [INSUFFICIENT_DATA]
