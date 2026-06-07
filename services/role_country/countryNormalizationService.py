"""Country normalization service."""

from services.role_country.rule_loader import load_json_config


class CountryNormalizationService:
    """Normalize country aliases using configured mappings."""

    def __init__(self, mappings: dict[str, str] | None = None) -> None:
        source = mappings or load_json_config("country_mappings.json")
        self._mappings = {key.casefold().strip(): value for key, value in source.items()}

    def normalize(self, country: object) -> str:
        """Return normalized country name or an empty string."""
        if country is None:
            return ""
        text = str(country).strip()
        if not text:
            return ""
        return self._mappings.get(text.casefold(), text.title())

