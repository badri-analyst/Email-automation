"""Company name normalization."""

import re
from collections.abc import Sequence

from core.constants import COMPANY_LEGAL_SUFFIXES


class CompanyNormalizer:
    """Normalize company names while preserving meaningful brand text."""

    def __init__(self, legal_suffixes: Sequence[str] = COMPANY_LEGAL_SUFFIXES) -> None:
        escaped = [re.escape(suffix).replace(r"\ ", r"\s+") for suffix in legal_suffixes]
        suffix_pattern = "|".join(sorted(escaped, key=len, reverse=True))
        self._suffix_pattern = re.compile(
            rf"(?:,|\s)+({suffix_pattern})\.?$",
            re.IGNORECASE,
        )

    def normalize(self, value: object) -> str:
        """Return a company name without common legal suffixes."""
        if value is None:
            return ""

        text = str(value).strip()
        previous = None
        while previous != text:
            previous = text
            text = self._suffix_pattern.sub("", text).strip(" ,.")
        return text

