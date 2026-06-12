"""Final personalization payload builder."""

from typing import Any

from schemas.decisionSchema import FinalPersonalizationPayload


class FinalPayloadBuilder:
    """Build approved downstream personalization payload from supported fields only."""

    def build(
        self,
        cleaning: dict[str, Any],
        role_country: dict[str, Any],
        linkedin: dict[str, Any],
        company: dict[str, Any],
        selected_path: str,
        candidate_profile: dict[str, Any] | None = None,
    ) -> FinalPersonalizationPayload:
        """Return final personalization payload with unsupported data omitted."""
        hooks: list[str] = []
        if selected_path in {"full_context", "company_fallback", "company_role_country"}:
            hooks.extend(self._non_insufficient_list(company.get("company_personalization_hooks", [])))
        if selected_path in {"full_context", "linkedin_role_country"}:
            hooks.extend(self._non_insufficient_list(linkedin.get("personalization_insights", [])))
        if selected_path in {"full_context", "role_country_only", "linkedin_role_country", "company_role_country", "company_fallback"}:
            hooks.extend(self._non_insufficient_list(role_country.get("personalization_guidance", [])))

        return FinalPersonalizationPayload(
            candidate=self._candidate(candidate_profile or {}),
            prospect=self._prospect(cleaning),
            role_country_context=self._allowed_role_country(role_country),
            linkedin_context=self._allowed_linkedin(linkedin) if selected_path in {"full_context", "linkedin_role_country"} else {},
            company_context=self._allowed_company(company) if selected_path in {"full_context", "company_fallback", "company_role_country"} else {},
            selected_hooks=list(dict.fromkeys(hooks))[:5],
            email_angle=company.get("company_email_angle") or role_country.get("email_positioning_angle", ""),
            things_to_avoid=self._non_insufficient_list(role_country.get("things_to_avoid", [])),
        )

    @staticmethod
    def _candidate(profile: dict[str, Any]) -> dict[str, Any]:
        """Return candidate fields needed by the email generation prompt."""
        return {
            "full_name": profile.get("fullName") or profile.get("full_name") or "",
            "email": profile.get("email") or "",
            "current_role": profile.get("currentRole") or profile.get("current_role") or "",
            "skills": profile.get("skills") or "",
            "resume_summary": profile.get("resumeSummary") or profile.get("resume_summary") or "",
            "why_relevant": profile.get("whyRelevant") or profile.get("why_relevant") or "",
            "linkedin_url": profile.get("linkedInUrl") or profile.get("linkedin_url") or "",
            "youtube_url": profile.get("youtubeUrl") or profile.get("youtube_url") or "",
            "github_url": profile.get("githubUrl") or profile.get("github_url") or "",
            "portfolio_url": profile.get("portfolioUrl") or profile.get("portfolio_url") or "",
            "preferred_countries": profile.get("preferredCountries") or profile.get("preferred_countries") or "",
        }

    @staticmethod
    def _prospect(cleaning: dict[str, Any]) -> dict[str, Any]:
        """Return allowed prospect fields."""
        return {
            "name": cleaning.get("full_name") or cleaning.get("name") or cleaning.get("Name"),
            "first_name": cleaning.get("first_name"),
            "email": cleaning.get("email") or cleaning.get("Email"),
            "company": cleaning.get("company_name") or cleaning.get("Company"),
            "role": cleaning.get("role_title") or cleaning.get("Role"),
            "country": cleaning.get("normalized_country") or cleaning.get("country") or cleaning.get("Country"),
        }

    @staticmethod
    def _allowed_role_country(data: dict[str, Any]) -> dict[str, Any]:
        """Return approved role-country context fields."""
        keys = [
            "normalized_role",
            "normalized_country",
            "role_summary",
            "core_responsibilities",
            "country_role_expectations",
            "priority_skills",
            "tools_or_frameworks",
            "business_keywords",
            "email_positioning_angle",
            "country_specific_email_tone",
            "proof_points_to_use",
        ]
        return {key: data.get(key) for key in keys if data.get(key) not in (None, "Insufficient data.")}

    @staticmethod
    def _allowed_linkedin(data: dict[str, Any]) -> dict[str, Any]:
        """Return approved LinkedIn research context fields."""
        keys = ["overview", "communication_style", "professional_motivators", "personalization_insights"]
        return {key: data.get(key) for key in keys if data.get(key)}

    @staticmethod
    def _allowed_company(data: dict[str, Any]) -> dict[str, Any]:
        """Return approved company research context fields."""
        keys = [
            "company_overview",
            "industry",
            "products_services_summary",
            "company_values_summary",
            "recent_company_updates",
            "growth_or_hiring_signal",
            "role_relevance_context",
            "country_relevance_context",
        ]
        return {key: data.get(key) for key in keys if data.get(key) not in (None, "Insufficient data.")}

    @staticmethod
    def _non_insufficient_list(values: list[Any]) -> list[str]:
        """Return non-empty, supported list values."""
        output: list[str] = []
        for value in values:
            if isinstance(value, str) and value and value != "Insufficient data.":
                output.append(value)
        return output
