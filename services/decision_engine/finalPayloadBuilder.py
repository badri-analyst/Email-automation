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
        personality: dict[str, Any],
        selected_path: str,
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
            prospect=self._prospect(cleaning),
            role_country_context=self._allowed_role_country(role_country),
            linkedin_context=self._allowed_linkedin(linkedin) if selected_path in {"full_context", "linkedin_role_country"} else {},
            company_context=self._allowed_company(company) if selected_path in {"full_context", "company_fallback", "company_role_country"} else {},
            personality_context=self._allowed_personality(personality) if selected_path == "full_context" else {},
            selected_hooks=list(dict.fromkeys(hooks))[:5],
            email_angle=company.get("company_email_angle") or role_country.get("email_positioning_angle", ""),
            things_to_avoid=self._non_insufficient_list(
                role_country.get("things_to_avoid", []) + [personality.get("persuasion_profile", {}).get("what_to_avoid", "")]
            ),
        )

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
    def _allowed_personality(data: dict[str, Any]) -> dict[str, Any]:
        """Return approved communication signal context fields."""
        keys = ["communication_style", "professional_behavioral_signals", "professional_motivators", "persuasion_profile"]
        return {key: data.get(key) for key in keys if data.get(key)}

    @staticmethod
    def _non_insufficient_list(values: list[Any]) -> list[str]:
        """Return non-empty, supported list values."""
        output: list[str] = []
        for value in values:
            if isinstance(value, str) and value and value != "Insufficient data.":
                output.append(value)
        return output
