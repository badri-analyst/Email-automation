"""Email positioning and guidance service."""

from schemas.roleCountrySchema import INSUFFICIENT_DATA


class EmailPositioningService:
    """Generate deterministic outreach positioning guidance from configured rules."""

    def guidance(
        self,
        role: str,
        country: str,
        angle: str,
        expectations: list[str],
        proof_points: list[str],
        candidate_positioning: str,
    ) -> list[str]:
        """Return three to five actionable personalization guidance points."""
        if angle == INSUFFICIENT_DATA:
            return [INSUFFICIENT_DATA]

        guidance = [
            angle,
            f"Emphasize {expectations[0]}." if expectations and expectations[0] != INSUFFICIENT_DATA else "Keep the email role-specific and evidence-based.",
            f"Use a proof point such as {proof_points[0]}." if proof_points and proof_points[0] != INSUFFICIENT_DATA else "Use a concrete, truthful proof point.",
        ]
        if candidate_positioning:
            guidance.append(f"Connect candidate positioning to the {role} opportunity: {candidate_positioning}.")
        if country:
            guidance.append(f"Keep the message appropriate for {country}: professional, concise, and supported by evidence.")
        return guidance[:5]
