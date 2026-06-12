"""Research path selection."""

from typing import Any

from services.decision_engine.rule_loader import load_decision_config


class ResearchPathSelector:
    """Select the best deterministic personalization path."""

    def __init__(self) -> None:
        self._rules = load_decision_config("decision_rules.json")

    def select(
        self,
        role_country: dict[str, Any],
        linkedin: dict[str, Any],
        company: dict[str, Any],
    ) -> tuple[str, str, str]:
        """Return selected path, source, and reason."""
        role_ready = role_country.get("role_country_status") in self._rules["role_country_ready_statuses"]
        linkedin_ready = linkedin.get("research_status") in self._rules["linkedin_ready_statuses"]
        company_ready = company.get("company_research_status") in self._rules["company_ready_statuses"]

        if linkedin_ready and company_ready and role_ready:
            return "full_context", "combined_context", "LinkedIn, company, and role-country context are available."
        if linkedin_ready and role_ready:
            return "linkedin_role_country", "linkedin_research", "Person-level LinkedIn research and role-country context are available."
        if company_ready and role_ready:
            return "company_role_country", "company_research", "Company context and role-country intelligence are available."
        if role_ready:
            return "role_country_only", "role_country_intelligence", "Only role-country intelligence is sufficiently available."
        return "insufficient_data", "none", "No sufficient personalization source is available."
