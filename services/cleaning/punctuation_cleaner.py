"""Outreach-safe punctuation sanitization."""

import re
import unicodedata


class PunctuationCleaner:
    """Remove unsupported control or malformed symbols while preserving safe punctuation."""

    _safe_symbols = set("@._:/?&=%+-'(),#")
    _space_pattern = re.compile(r"\s+")

    def clean(self, value: object) -> str:
        """Return text with unsafe control and malformed symbols removed."""
        if value is None:
            return ""

        output: list[str] = []
        for char in str(value):
            category = unicodedata.category(char)
            if char.isspace():
                output.append(" ")
            elif category.startswith(("L", "N")) or char in self._safe_symbols:
                output.append(char)
            elif category.startswith("P"):
                output.append(char)
            elif category.startswith("S"):
                continue
            elif category.startswith("C"):
                continue
            else:
                output.append(char)

        return self._space_pattern.sub(" ", "".join(output)).strip()
