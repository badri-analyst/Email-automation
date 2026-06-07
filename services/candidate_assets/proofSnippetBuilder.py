"""Candidate proof snippet builder."""

from schemas.candidateAssetsSchema import INSUFFICIENT_PROOF


class ProofSnippetBuilder:
    """Build concise proof snippets from candidate-provided proof points only."""

    _unsafe_terms = ("%", "increased", "doubled", "best", "guaranteed", "top")

    def build(self, proof_points: list[str]) -> tuple[list[str], bool]:
        """Return proof snippets and manual review flag."""
        snippets: list[str] = []
        manual_review = False
        for proof in proof_points:
            cleaned = self._clean(proof)
            if not cleaned:
                continue
            if any(term in cleaned.casefold() for term in self._unsafe_terms):
                manual_review = True
            snippets.append(cleaned[:140].rstrip())
            if len(snippets) == 4:
                break
        return (snippets or [INSUFFICIENT_PROOF]), manual_review

    @staticmethod
    def _clean(text: str) -> str:
        """Clean proof point text without inventing detail."""
        return " ".join(str(text).replace("<", "").replace(">", "").split())
