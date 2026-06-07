"""Candidate positioning builder."""


class CandidatePositioningService:
    """Position the candidate quickly using the required formula."""

    def build(self, payload: dict) -> str:
        """Return candidate positioning sentence."""
        prospect = payload.get("prospect", {})
        role_context = payload.get("role_country_context", {})
        role = prospect.get("role") or role_context.get("normalized_role") or "Business Analyst"
        keywords = role_context.get("business_keywords") or ["workflow clarity"]
        outcome = keywords[0] if isinstance(keywords, list) and keywords else "workflow clarity"
        return f"I am a {role} focused on {outcome}."
