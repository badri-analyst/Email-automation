"""Opening personalization trigger selection."""


class OpeningTriggerSelector:
    """Select strongest safe opening personalization source."""

    def select(self, payload: dict) -> tuple[str, str, dict[str, bool]]:
        """Return opening line, trigger, and source flags."""
        sources = {
            "linkedin_context_used": False,
            "company_context_used": False,
            "role_country_context_used": False,
            "personality_guidance_used": False,
            "fallback_used": False,
        }
        linkedin = payload.get("linkedin_context", {})
        company = payload.get("company_context", {})
        role_country = payload.get("role_country_context", {})

        linkedin_insights = linkedin.get("personalization_insights") or []
        if linkedin_insights:
            sources["linkedin_context_used"] = True
            return self._line(linkedin_insights[0]), "LinkedIn professional context", sources

        hooks = payload.get("selected_hooks") or []
        if hooks:
            sources["company_context_used"] = bool(company)
            sources["role_country_context_used"] = bool(role_country)
            return self._line(hooks[0]), "approved personalization hook", sources

        if role_country.get("email_positioning_angle"):
            sources["role_country_context_used"] = True
            return self._line(role_country["email_positioning_angle"]), "role-country relevance", sources

        sources["fallback_used"] = True
        return "I wanted to reach out with a focused note about Business Analyst opportunities.", "role-based fallback", sources

    @staticmethod
    def _line(text: str) -> str:
        """Return one concise opening sentence."""
        sentence = str(text).split(".")[0].strip()
        return f"{sentence}." if sentence else "I wanted to reach out with a focused note."
