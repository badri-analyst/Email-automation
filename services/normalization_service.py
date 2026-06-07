"""Reusable normalization services."""

import re

import pandas as pd

from core.constants import COUNTRY_NORMALIZATION_MAP


class CountryNormalizationService:
    """Normalize country names with a dictionary mapping strategy."""

    def __init__(self, country_mapping: dict[str, str] | None = None) -> None:
        self._country_mapping = country_mapping or COUNTRY_NORMALIZATION_MAP

    def normalize_country(self, value: object) -> object:
        """Normalize a single country value."""
        if pd.isna(value):
            return value

        text = re.sub(r"\s+", " ", str(value).strip())
        if not text:
            return ""

        return self._country_mapping.get(text.casefold(), text)

    def normalize_series(self, series: pd.Series) -> pd.Series:
        """Normalize a pandas Series of country values."""
        return series.map(self.normalize_country)
