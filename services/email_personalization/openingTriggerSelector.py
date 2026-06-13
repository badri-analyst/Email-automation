"""Opening personalization trigger selection."""


class OpeningTriggerSelector:
    """Select strongest safe opening from FinalPersonalizationPayload."""

    def select(self, payload: dict) -> tuple[str, str, dict[str, bool]]:
        """Return opening line, trigger type, and source flags."""
        sources = {
            "linkedin_context_used": False,
            "company_context_used": False,
            "role_country_context_used": False,
            "personality_guidance_used": False,
            "fallback_used": False,
        }

        opening_hook = str(payload.get("opening_hook") or "").strip()
        if opening_hook:
            sources["linkedin_context_used"] = True
            return self._line(opening_hook), "opening hook", sources

        key_skills = payload.get("key_skills") or []
        if key_skills:
            sources["role_country_context_used"] = True
            skill = key_skills[0]
            prospect = payload.get("prospect", {})
            role = prospect.get("role") or "this role"
            return f"I came across your opening for {role} and wanted to reach out — {skill} is something I have been focused on.", "key skill relevance", sources

        sources["fallback_used"] = True
        prospect = payload.get("prospect", {})
        role = prospect.get("role") or "Business Analyst"
        return f"I wanted to reach out with a focused note about {role} opportunities.", "role-based fallback", sources

    @staticmethod
    def _line(text: str) -> str:
        sentence = str(text).split(".")[0].strip()
        return f"{sentence}." if sentence else "I wanted to reach out with a focused note."
