"""Rule-based department inference."""

from collections.abc import Mapping

from core.constants import DEPARTMENT_KEYWORD_MAP


class DepartmentInference:
    """Infer deterministic departments from role titles."""

    def __init__(self, keyword_mapping: Mapping[str, tuple[str, ...]] | None = None) -> None:
        self._keyword_mapping = keyword_mapping or DEPARTMENT_KEYWORD_MAP

    def infer(self, role_title: object) -> str:
        """Return the inferred department or unknown."""
        if role_title is None:
            return "unknown"

        normalized = str(role_title).casefold()
        for department, keywords in self._keyword_mapping.items():
            if any(keyword.casefold() in normalized for keyword in keywords):
                return department
        return "unknown"

