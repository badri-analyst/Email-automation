"""Why relevant summary builder."""

from schemas.candidateAssetsSchema import INSUFFICIENT_PROOF


class WhyRelevantBuilder:
    """Build low-pressure relevance summaries."""

    def build(self, proof_snippets: list[str], positioning_summary: str) -> str:
        """Return safe relevance summary."""
        valid_snippets = [snippet for snippet in proof_snippets if snippet != INSUFFICIENT_PROOF]
        if valid_snippets:
            return f"May be relevant because of experience related to {valid_snippets[0].lower()}."
        if positioning_summary != INSUFFICIENT_PROOF:
            return f"May be relevant based on positioning around {positioning_summary.lower()}"
        return INSUFFICIENT_PROOF
