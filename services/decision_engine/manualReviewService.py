"""Manual review requirement checks."""

from typing import Any

from services.decision_engine.rule_loader import load_decision_config


class ManualReviewService:
    """Evaluate manual review requirements from upstream status and guardrails."""

    def __init__(self) -> None:
        self._rules = load_decision_config("decision_rules.json")

    def evaluate(
        self,
        removed_score_fields: list[str],
        personality: dict[str, Any],
        company: dict[str, Any],
        role_country: dict[str, Any],
    ) -> tuple[bool, str]:
        """Return manual review flag and reason."""
        if removed_score_fields:
            return True, f"Forbidden score/rating/ranking fields were removed: {', '.join(removed_score_fields)}."
        if personality.get("manual_review_flag") is True:
            return True, personality.get("personality_analysis_reason", "Personality analysis requested manual review.")
        if company.get("manual_review_flag") is True:
            return True, company.get("company_research_reason", "Company research requested manual review.")
        if role_country.get("role_country_status") in self._rules["manual_review_statuses"]:
            return True, role_country.get("role_country_reason", "Role-country intelligence requested manual review.")
        if personality.get("personality_analysis_status") in self._rules["manual_review_statuses"]:
            return True, personality.get("personality_analysis_reason", "Personality analysis requested manual review.")
        return False, ""
