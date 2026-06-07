"""Role-country status assignment service."""


class RoleCountryStatusService:
    """Assign deterministic role-country intelligence statuses."""

    def assign(
        self,
        has_role: bool,
        role_supported: bool,
        has_country: bool,
        country_supported: bool,
        industry_used: bool,
        seniority_used: bool,
    ) -> tuple[str, str]:
        """Return status and reason."""
        if not has_role:
            return "role_missing", "Target role is missing."
        if not role_supported:
            return "role_country_not_supported", "Configured role guidance is unavailable."
        if not has_country:
            return "role_only_intelligence_used", "Country is missing; role-only intelligence was used."
        if not country_supported:
            return "country_missing", "Configured country guidance is unavailable; role-only intelligence was used."
        if industry_used:
            return "industry_refinement_used", "Industry-specific configured refinement was applied."
        if seniority_used:
            return "seniority_refinement_used", "Seniority-specific configured refinement was applied."
        return "ready_for_personalization", "Configured role-country intelligence is available."
