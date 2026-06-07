"""Safety filtering for communication analysis outputs."""

from safety.sensitiveContentFilter import SensitiveContentFilter
from safety.unsafeInferenceBlocker import UnsafeInferenceBlocker


class SafetyFilterService:
    """Block unsafe inference and flag invasive wording."""

    _manual_review_terms = ("creepy", "invasive", "overly personal", "uncertain", "private")

    def __init__(self) -> None:
        self._sensitive_filter = SensitiveContentFilter()
        self._unsafe_blocker = UnsafeInferenceBlocker()

    def is_blocked(self, *texts: object) -> bool:
        """Return True when any text contains forbidden inference language."""
        return any(
            self._unsafe_blocker.is_unsafe(text) or self._sensitive_filter.contains_sensitive_inference(text)
            for text in texts
        )

    def requires_manual_review(self, *texts: object) -> bool:
        """Return True when output may sound invasive or uncertain."""
        combined = " ".join("" if text is None else str(text) for text in texts).casefold()
        return any(term in combined for term in self._manual_review_terms)
