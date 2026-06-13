"""Final personalization payload builder."""

from typing import Any

from schemas.decisionSchema import FinalPersonalizationPayload


class FinalPayloadBuilder:
    """Build the final payload the email generation prompt reads from."""

    def build(
        self,
        cleaning: dict[str, Any],
        role_country: dict[str, Any],
        linkedin: dict[str, Any],
        company: dict[str, Any],
        candidate_profile: dict[str, Any] | None = None,
    ) -> FinalPersonalizationPayload:
        """Synthesise all research outputs into one clean email-ready payload."""
        return FinalPersonalizationPayload(
            opening_hook=self._pick_hook(linkedin, company, role_country),
            candidate=self._candidate(candidate_profile or {}),
            prospect=self._prospect(cleaning),
            key_skills=self._key_skills(role_country),
            tone_guidance=self._tone_guidance(role_country, linkedin),
        )

    # ------------------------------------------------------------------
    # Hook selection — LinkedIn first → company second → role-country fallback
    # Only use a source if its key field is not empty or "Insufficient data."
    # ------------------------------------------------------------------
    @staticmethod
    def _pick_hook(
        linkedin: dict[str, Any],
        company: dict[str, Any],
        role_country: dict[str, Any],
    ) -> str:
        """Return the best opening hook from available sources."""
        def valid(value: Any) -> bool:
            return bool(value) and str(value).strip() not in ("", "Insufficient data.")

        # 1. LinkedIn personal hook — most specific to this individual
        linkedin_hooks = linkedin.get("personalization_insights", [])
        if isinstance(linkedin_hooks, list):
            for hook in linkedin_hooks:
                if valid(hook):
                    return str(hook).strip()

        # 2. Company hook — funding / launch / hiring signal
        company_hooks = company.get("company_personalization_hooks", [])
        if isinstance(company_hooks, list):
            for hook in company_hooks:
                if valid(hook):
                    return str(hook).strip()

        # 3. Role-country focus — least personal but always available
        focus = role_country.get("email_positioning_angle", "") or role_country.get("country_specific_email_tone", "")
        if valid(focus):
            return str(focus).strip()

        return ""

    # ------------------------------------------------------------------
    # Key skills — exact job market phrases from role-country intelligence
    # ------------------------------------------------------------------
    @staticmethod
    def _key_skills(role_country: dict[str, Any]) -> list[str]:
        """Return top 3 exact phrases hiring managers use in this country/role."""
        # priority_skills has the most specific job-market phrases
        phrases = role_country.get("priority_skills", []) or role_country.get("business_keywords", [])
        if not isinstance(phrases, list):
            return []
        result = [
            str(p).strip() for p in phrases
            if p and str(p).strip() not in ("", "Insufficient data.")
        ]
        return result[:3]

    # ------------------------------------------------------------------
    # Tone guidance — country focus + what to avoid from LinkedIn profile
    # ------------------------------------------------------------------
    @staticmethod
    def _tone_guidance(role_country: dict[str, Any], linkedin: dict[str, Any]) -> str:
        """Return tone guidance for the email writer."""
        parts: list[str] = []

        focus = role_country.get("country_specific_email_tone", "") or role_country.get("email_positioning_angle", "")
        if focus and focus.strip() not in ("", "Insufficient data."):
            parts.append(focus.strip())

        avoid = linkedin.get("persuasion_profile", {}).get("what_to_avoid", "")
        if avoid and avoid.strip() not in ("", "Insufficient data."):
            parts.append(f"Avoid: {avoid.strip()}")

        return " | ".join(parts)

    # ------------------------------------------------------------------
    # Candidate — from saved profile form
    # ------------------------------------------------------------------
    @staticmethod
    def _candidate(profile: dict[str, Any]) -> dict[str, Any]:
        """Return candidate fields needed by the email generation prompt."""
        return {
            "full_name": profile.get("fullName") or profile.get("full_name") or "",
            "current_role": profile.get("currentRole") or profile.get("current_role") or "",
            "skills": profile.get("skills") or "",
            "why_relevant": profile.get("whyRelevant") or profile.get("why_relevant") or "",
            "linkedin_url": profile.get("linkedInUrl") or profile.get("linkedin_url") or "",
            "youtube_url": profile.get("youtubeUrl") or profile.get("youtube_url") or "",
            "portfolio_url": profile.get("portfolioUrl") or profile.get("portfolio_url") or "",
        }

    # ------------------------------------------------------------------
    # Prospect — from cleaning output (row data)
    # ------------------------------------------------------------------
    @staticmethod
    def _prospect(cleaning: dict[str, Any]) -> dict[str, Any]:
        """Return prospect fields for the email generation prompt."""
        return {
            "name": cleaning.get("full_name") or cleaning.get("name") or cleaning.get("Name") or "",
            "email": cleaning.get("email") or cleaning.get("Email") or "",
            "company": cleaning.get("company_name") or cleaning.get("Company") or "",
            "role": cleaning.get("role_title") or cleaning.get("Role") or "",
            "country": cleaning.get("normalized_country") or cleaning.get("country") or cleaning.get("Country") or "",
        }
