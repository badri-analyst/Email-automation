"""Sensitive and private inference filters."""

import re


class SensitiveContentFilter:
    """Detect sensitive inference language that must not be generated."""

    _sensitive_patterns = (
        r"\b(age|gender|religion|politics|ethnicity|sexuality|family status|health|medical|mental health)\b",
        r"\b(anxious|depressed|narcissistic|introvert|extrovert|personality disorder)\b",
    )

    def contains_sensitive_inference(self, text: object) -> bool:
        """Return True when text contains forbidden sensitive inference terms."""
        value = "" if text is None else str(text).casefold()
        return any(re.search(pattern, value, re.IGNORECASE) for pattern in self._sensitive_patterns)
