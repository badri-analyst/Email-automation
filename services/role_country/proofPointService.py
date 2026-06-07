"""Proof point recommendation service."""

from schemas.roleCountrySchema import INSUFFICIENT_DATA


class ProofPointService:
    """Build proof-point recommendations from role and refinements."""

    @staticmethod
    def build(base_proof_points: list[str], refinements: list[str]) -> list[str]:
        """Return deterministic proof points."""
        output = [item for item in base_proof_points if item and item != INSUFFICIENT_DATA]
        for refinement in refinements:
            output.append(f"{refinement} example")
        return list(dict.fromkeys(output)) or [INSUFFICIENT_DATA]
