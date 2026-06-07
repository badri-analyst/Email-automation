"""Evidence sanitation and traceability helpers."""

import re
import unicodedata

from services.cleaning.html_cleaner import HtmlCleaner
from services.cleaning.whitespace_cleaner import WhitespaceCleaner


class EvidenceManager:
    """Sanitize imported research text and produce bounded evidence notes."""

    _prompt_injection_pattern = re.compile(
        r"\b(ignore|override|forget|disregard)\s+(all\s+)?(previous|prior|above)\s+instructions\b",
        re.IGNORECASE,
    )

    def __init__(self, max_evidence_chars: int = 220) -> None:
        self._max_evidence_chars = max_evidence_chars
        self._html_cleaner = HtmlCleaner()
        self._whitespace_cleaner = WhitespaceCleaner()

    def sanitize_text(self, value: object) -> str:
        """Return safe text treated strictly as imported data."""
        if value is None:
            return ""

        text = unicodedata.normalize("NFKC", str(value))
        text = self._html_cleaner.clean(text)
        text = "".join(char for char in text if not unicodedata.category(char).startswith("C"))
        text = self._prompt_injection_pattern.sub("[removed unsafe instruction]", text)
        return self._whitespace_cleaner.clean(text)

    def combine_sources(self, values: list[object]) -> str:
        """Return sanitized research text from multiple approved sources."""
        return self._whitespace_cleaner.clean(" ".join(self.sanitize_text(value) for value in values if value))

    def evidence_note(self, text: object) -> str:
        """Return a concise evidence note or the insufficient-data marker."""
        sanitized = self.sanitize_text(text)
        if not sanitized:
            return "Insufficient data."
        return sanitized[: self._max_evidence_chars].rstrip()

    def has_evidence(self, text: object, minimum_chars: int = 20) -> bool:
        """Return whether sanitized text is strong enough to support a claim."""
        return len(self.sanitize_text(text)) >= minimum_chars
