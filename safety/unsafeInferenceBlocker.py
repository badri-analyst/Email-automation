"""Unsafe inference blocker for communication analysis."""

import re


class UnsafeInferenceBlocker:
    """Block manipulative, diagnostic, or scoring language."""

    _unsafe_patterns = (
        r"\b(personality_score|psychology_score|influence_score|persuasion_score|confidence_score|lead_score|fit_score)\b",
        r"\b(manipulate|exploit|pressure|guilt|fear|dark psychology|diagnose|psychological profile)\b",
        r"\b(ranking|rating|score)\b",
    )

    def is_unsafe(self, text: object) -> bool:
        """Return True when text contains unsafe analysis language."""
        value = "" if text is None else str(text).casefold()
        return any(re.search(pattern, value, re.IGNORECASE) for pattern in self._unsafe_patterns)
