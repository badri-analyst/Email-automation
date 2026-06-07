"""Candidate proof-point selection."""


class CandidateProofPointService:
    """Use only supported proof points from upstream context."""

    def build(self, payload: dict) -> str:
        """Return proof point sentence or a safe fallback value sentence."""
        role_context = payload.get("role_country_context", {})
        proof_points = role_context.get("proof_points_to_use") or []
        if proof_points:
            return f"I can share a relevant {proof_points[0]} tied to stakeholder alignment and workflow clarity."
        return "I can share a concise example of how I approach stakeholder alignment and workflow clarity."
