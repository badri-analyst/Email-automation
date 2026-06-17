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
        profile = candidate_profile or {}
        return FinalPersonalizationPayload(
            opening_hook=self._pick_hook(company),
            candidate=self._candidate(profile),
            prospect=self._prospect(cleaning),
            key_skills=self._pick_skills(profile, company),
            tone_guidance=self._pick_tone(company, cleaning),
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
    # Key skills — from candidate profile, max 3
    # ------------------------------------------------------------------
    @staticmethod
    def _pick_skills(profile: dict[str, Any], company: dict[str, Any]) -> list[str]:
        raw = profile.get("skills") or profile.get("key_skills") or ""
        if isinstance(raw, list):
            skills = [s.strip() for s in raw if s.strip()]
        else:
            skills = [s.strip() for s in str(raw).split(",") if s.strip()]
        # Supplement with role relevance context from company research if few skills
        if len(skills) < 2:
            role_ctx = company.get("role_relevance_context", "")
            if role_ctx and role_ctx != "Insufficient data.":
                skills.append(role_ctx[:80])
        return skills[:3]

    # ------------------------------------------------------------------
    # Tone guidance — from company research
    # ------------------------------------------------------------------
    @staticmethod
    def _pick_tone(company: dict[str, Any], cleaning: dict[str, Any]) -> str:
        angle = company.get("company_email_angle", "")
        if angle and angle != "Insufficient data.":
            return angle
        country = cleaning.get("normalized_country") or cleaning.get("country") or ""
        if country:
            return f"Professional tone suitable for {country} business culture."
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
