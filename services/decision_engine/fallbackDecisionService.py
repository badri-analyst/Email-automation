"""Fallback decision service."""

from typing import Any

from services.decision_engine.rule_loader import load_decision_config


class FallbackDecisionService:
    """Determine fallback usage from selected path and upstream statuses."""

    def __init__(self) -> None:
        self._rules = load_decision_config("decision_rules.json")

    def evaluate(self, selected_path: str, linkedin: dict[str, Any]) -> tuple[bool, str, str]:
        """Return fallback flag, fallback path, and reason."""
        linkedin_status = linkedin.get("research_status", "")
        if selected_path == "company_role_country" and linkedin_status in self._rules["linkedin_weak_statuses"]:
            return True, "company_fallback", "LinkedIn research was weak or unavailable; company fallback selected."
        if selected_path == "role_country_only":
            return True, "role_country_only", "Person and company research were weak; role-country-only fallback selected."
        return False, selected_path, ""
