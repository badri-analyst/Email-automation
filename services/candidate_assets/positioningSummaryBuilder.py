"""Professional positioning summary builder."""

from schemas.candidateAssetsSchema import INSUFFICIENT_PROOF


class PositioningSummaryBuilder:
    """Build concise factual positioning from candidate-provided text."""

    def build(self, candidate_positioning: str, target_role: str, role_country_positioning: str) -> str:
        """Return recruiter-safe professional positioning summary."""
        source = self._clean(candidate_positioning)
        if source:
            return source[:180].rstrip()
        if target_role and role_country_positioning:
            return f"{target_role} focused on {self._clean(role_country_positioning).lower()}."[:180].rstrip()
        if target_role:
            return f"{target_role} focused on workflow clarity and stakeholder alignment."
        return INSUFFICIENT_PROOF

    @staticmethod
    def _clean(text: str) -> str:
        """Clean positioning text."""
        return " ".join(str(text).replace("<", "").replace(">", "").split())
