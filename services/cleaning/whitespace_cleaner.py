"""Whitespace normalization for outreach text fields."""

import re


class WhitespaceCleaner:
    """Trim leading/trailing whitespace and compress repeated whitespace."""

    _whitespace_pattern = re.compile(r"\s+")

    def clean(self, value: object) -> str:
        """Return a whitespace-normalized string."""
        if value is None:
            return ""
        text = str(value)
        if text.casefold() in {"nan", "none", "null"}:
            return ""
        return self._whitespace_pattern.sub(" ", text.strip())

