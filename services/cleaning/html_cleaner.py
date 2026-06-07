"""HTML and script tag cleanup."""

import html
import re


class HtmlCleaner:
    """Remove HTML tags and decode HTML entities without executing content."""

    _script_style_pattern = re.compile(r"<\s*(script|style).*?>.*?<\s*/\s*\1\s*>", re.IGNORECASE | re.DOTALL)
    _tag_pattern = re.compile(r"<[^>]+>")

    def clean(self, value: object) -> str:
        """Return text with tags removed and entities decoded."""
        if value is None:
            return ""

        text = html.unescape(str(value))
        text = self._script_style_pattern.sub(" ", text)
        return self._tag_pattern.sub(" ", text)

