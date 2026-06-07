"""Candidate proof status assignment."""

from schemas.candidateAssetsSchema import INSUFFICIENT_PROOF


class ProofStatusService:
    """Assign deterministic proof status and reason."""

    def assign(
        self,
        linkedin_status: str,
        resume_available: bool,
        video_count: int,
        portfolio_count: int,
        snippets: list[str],
        invalid_links: bool,
        manual_review: bool,
    ) -> tuple[str, str]:
        """Return proof status and reason."""
        if manual_review:
            return "manual_review_required", "Proof assets require manual review for unsupported or risky claims."
        if invalid_links:
            return "invalid_asset_link", "One or more candidate asset links were invalid."
        proof_count = sum(
            [
                linkedin_status == "valid",
                resume_available,
                video_count > 0,
                portfolio_count > 0,
                bool(snippets and snippets != [INSUFFICIENT_PROOF]),
            ]
        )
        if proof_count >= 3:
            return "proof_ready", "Candidate proof assets are ready."
        if proof_count >= 1:
            return "partial_proof_available", "Partial candidate proof is available."
        return "insufficient_supporting_proof", INSUFFICIENT_PROOF
