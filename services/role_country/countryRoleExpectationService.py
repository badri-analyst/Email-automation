"""Country-specific role expectation lookup."""

from typing import Any

from schemas.roleCountrySchema import INSUFFICIENT_DATA
from services.role_country.rule_loader import load_json_config


class CountryRoleExpectationService:
    """Return approved country-level professional expectations."""

    def __init__(self, rules: dict[str, Any] | None = None) -> None:
        self._rules = rules or load_json_config("role_country_rules.json")

    def is_supported(self, normalized_country: str) -> bool:
        """Return whether country guidance exists."""
        return normalized_country in self._rules.get("countries", {})

    def expectations(self, normalized_country: str) -> list[str]:
        """Return country expectations from configured rules."""
        return self._country(normalized_country).get("expectations", [INSUFFICIENT_DATA])

    def email_tone(self, normalized_country: str) -> str:
        """Return country-specific professional tone guidance."""
        return self._country(normalized_country).get("email_tone", INSUFFICIENT_DATA)

    def _country(self, normalized_country: str) -> dict[str, Any]:
        """Return country config."""
        return self._rules.get("countries", {}).get(normalized_country, {})

