"""Rule-based seniority inference."""

from collections.abc import Mapping

from core.constants import SENIORITY_KEYWORD_MAP


class SeniorityInference:
    """Infer deterministic seniority levels from role titles."""

    def __init__(self, keyword_mapping: Mapping[str, tuple[str, ...]] | None = None) -> None:
        self._keyword_mapping = keyword_mapping or SENIORITY_KEYWORD_MAP

    def infer(self, role_title: object) -> str:
        """Return the inferred seniority level or unknown."""
        if role_title is None:
            return "unknown"

        normalized = f" {str(role_title).casefold()} "
        for level, keywords in self._keyword_mapping.items():
            for keyword in keywords:
                key = keyword.casefold()
                if f" {key} " in normalized or normalized.strip() == key:
                    return level
        return "unknown"

