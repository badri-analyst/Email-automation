"""Forbidden score/rating/ranking field guard."""

from copy import deepcopy
from typing import Any

from services.decision_engine.rule_loader import load_decision_config


class ScoreFieldGuardService:
    """Remove forbidden scoring fields and report whether any were detected."""

    def __init__(self, patterns: list[str] | None = None) -> None:
        rules = load_decision_config("decision_rules.json")
        self._patterns = [pattern.casefold() for pattern in (patterns or rules["forbidden_field_patterns"])]

    def sanitize(self, payload: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
        """Return payload with forbidden score-like fields removed."""
        removed: list[str] = []
        sanitized = self._sanitize_value(deepcopy(payload), removed, "")
        return sanitized if isinstance(sanitized, dict) else {}, removed

    def _sanitize_value(self, value: Any, removed: list[str], path: str) -> Any:
        """Recursively sanitize dictionaries and lists."""
        if isinstance(value, dict):
            output: dict[str, Any] = {}
            for key, item in value.items():
                field_path = f"{path}.{key}" if path else str(key)
                if self._is_forbidden(str(key)):
                    removed.append(field_path)
                    continue
                output[key] = self._sanitize_value(item, removed, field_path)
            return output
        if isinstance(value, list):
            return [self._sanitize_value(item, removed, path) for item in value]
        return value

    def _is_forbidden(self, key: str) -> bool:
        """Return True when key matches forbidden score/ranking patterns."""
        lowered = key.casefold()
        return any(pattern in lowered for pattern in self._patterns)
