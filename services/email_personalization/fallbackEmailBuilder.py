"""Fallback email builder."""


class FallbackEmailBuilder:
    """Build role-based fallback email when personalization is weak."""

    def build(self, payload: dict, cta_sentence: str) -> str:
        """Return fallback role-based email body."""
        prospect = payload.get("prospect", {})
        role = prospect.get("role") or payload.get("role_country_context", {}).get("normalized_role") or "Business Analyst"
        return "\n\n".join(
            [
                f"I wanted to reach out with a focused note about {role} opportunities.",
                f"I am a {role} focused on workflow clarity and stakeholder alignment.",
                "I can share a concise example of how I approach requirements clarity, prioritization, and business-tech communication.",
                "I attached my resume in case it is relevant.",
                cta_sentence,
            ]
        )
