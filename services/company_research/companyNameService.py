"""Company name normalization service."""

import re

from core.constants import COMPANY_LEGAL_SUFFIXES


class CompanyNameService:
    """Normalize company names while preserving original values separately."""

    def __init__(self, legal_suffixes: tuple[str, ...] = COMPANY_LEGAL_SUFFIXES) -> None:
        escaped = [re.escape(suffix).replace(r"\ ", r"\s+") for suffix in legal_suffixes]
        suffix_pattern = "|".join(sorted(escaped, key=len, reverse=True))
        self._suffix_pattern = re.compile(rf"(?:,|\s)+({suffix_pattern})\.?$", re.IGNORECASE)

    def normalize(self, company_name: object) -> str:
        """Return a display-safe company name with legal suffixes removed."""
        if company_name is None:
            return ""
        text = str(company_name).strip()
        previous = None
        while previous != text:
            previous = text
            text = self._suffix_pattern.sub("", text).strip(" ,.")
        return " ".join(token if token.isupper() and len(token) <= 3 else token.capitalize() for token in text.split())
