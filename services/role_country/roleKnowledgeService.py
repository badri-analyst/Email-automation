"""Role knowledge lookup service."""

from typing import Any

from schemas.roleCountrySchema import INSUFFICIENT_DATA
from services.role_country.rule_loader import load_json_config


class RoleKnowledgeService:
    """Return configured role intelligence."""

    def __init__(self, rules: dict[str, Any] | None = None) -> None:
        self._rules = rules or load_json_config("role_country_rules.json")

    def is_supported(self, normalized_role: str) -> bool:
        """Return whether configured role knowledge exists."""
        return normalized_role in self._rules.get("roles", {})

    def role_summary(self, normalized_role: str) -> str:
        """Return role summary."""
        return self._role(normalized_role).get("summary", INSUFFICIENT_DATA)

    def core_responsibilities(self, normalized_role: str) -> list[str]:
        """Return core responsibilities."""
        return self._role(normalized_role).get("core_responsibilities", [INSUFFICIENT_DATA])

    def priority_skills(self, normalized_role: str) -> list[str]:
        """Return priority skills."""
        return self._role(normalized_role).get("priority_skills", [INSUFFICIENT_DATA])

    def tools_or_frameworks(self, normalized_role: str) -> list[str]:
        """Return tools/frameworks."""
        return self._role(normalized_role).get("tools_or_frameworks", [INSUFFICIENT_DATA])

    def business_keywords(self, normalized_role: str) -> list[str]:
        """Return business keywords."""
        return self._role(normalized_role).get("business_keywords", [INSUFFICIENT_DATA])

    def positioning_angle(self, normalized_role: str) -> str:
        """Return role positioning angle."""
        return self._role(normalized_role).get("positioning_angle", INSUFFICIENT_DATA)

    def proof_points(self, normalized_role: str) -> list[str]:
        """Return configured proof points."""
        return self._role(normalized_role).get("proof_points", [INSUFFICIENT_DATA])

    def things_to_avoid(self) -> list[str]:
        """Return safe outreach anti-patterns."""
        return self._rules.get("things_to_avoid", [INSUFFICIENT_DATA])

    def industry_refinement(self, industry: str) -> list[str]:
        """Return industry refinements."""
        if not industry:
            return []
        return self._rules.get("industry_refinements", {}).get(industry.casefold(), [])

    def seniority_refinement(self, seniority_level: str) -> list[str]:
        """Return seniority refinements."""
        if not seniority_level:
            return []
        return self._rules.get("seniority_refinements", {}).get(seniority_level.casefold(), [])

    def _role(self, normalized_role: str) -> dict[str, Any]:
        """Return role config."""
        return self._rules.get("roles", {}).get(normalized_role, {})

