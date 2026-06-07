"""Role normalization service."""

from services.role_country.rule_loader import load_json_config


class RoleNormalizationService:
    """Normalize role aliases using configured mappings."""

    def __init__(self, mappings: dict[str, str] | None = None) -> None:
        source = mappings or load_json_config("role_mappings.json")
        self._mappings = {key.casefold().strip(): value for key, value in source.items()}

    def normalize(self, role: object) -> str:
        """Return normalized role name or an empty string."""
        if role is None:
            return ""
        text = str(role).strip()
        if not text:
            return ""
        return self._mappings.get(text.casefold(), text.title())

