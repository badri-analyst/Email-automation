"""Final personalization payload builder."""

from typing import Any

from schemas.decisionSchema import FinalPersonalizationPayload


class FinalPayloadBuilder:
    """Build the final payload the email generation prompt reads from."""

    def build(
        self,
        cleaning: dict[str, Any],
        company: dict[str, Any],
        candidate_profile: dict[str, Any] | None = None,
    ) -> FinalPersonalizationPayload:
        """Synthesise company research and prospect data into one email-ready payload."""
        return FinalPersonalizationPayload(
            opening_hook=self._pick_hook(company),
            candidate=self._candidate(candidate_profile or {}),
            prospect=self._prospect(cleaning),
            key_skills=[],
            tone_guidance="",
        )

    # ------------------------------------------------------------------
    # Hook selection — LinkedIn first → company second → role-country fallback
    # Only use a source if its key field is not empty or "Insufficient data."
    # ------------------------------------------------------------------
    @staticmethod
    def _pick_hook(company: dict[str, Any]) -> str:
        """Return the best opening hook from company research."""
        def valid(value: Any) -> bool:
            return bool(value) and str(value).strip() not in ("", "Insufficient data.")

        company_hooks = company.get("company_personalization_hooks", [])
        if isinstance(company_hooks, list):
            for hook in company_hooks:
                if valid(hook):
                    return str(hook).strip()

        return ""

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
            "resume_url": profile.get("resumeUrl") or profile.get("resume_url") or "",
            "target_role": profile.get("targetRole") or profile.get("target_role") or "",
            "phone": profile.get("phone") or "",
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
