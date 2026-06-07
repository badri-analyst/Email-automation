"""Unicode cleanup that removes hidden formatting characters safely."""

import unicodedata


class UnicodeCleaner:
    """Remove invisible unicode characters while preserving valid unicode text."""

    _explicit_invisible_chars = {
        "\u200b",
        "\u200c",
        "\u200d",
        "\ufeff",
        "\u2060",
    }

    def clean(self, value: object) -> str:
        """Return text without zero-width or hidden formatting characters."""
        if value is None:
            return ""

        text = str(value)
        normalized = unicodedata.normalize("NFKC", text)
        return "".join(
            char
            for char in normalized
            if char not in self._explicit_invisible_chars and unicodedata.category(char) != "Cf"
        )

