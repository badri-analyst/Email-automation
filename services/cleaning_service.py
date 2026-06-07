"""Data cleaning pipeline."""

import re

import pandas as pd

from services.normalization_service import CountryNormalizationService


class CleaningService:
    """Clean dataframe values using vectorized pandas operations."""

    def __init__(self, country_normalizer: CountryNormalizationService | None = None) -> None:
        self._country_normalizer = country_normalizer or CountryNormalizationService()

    def clean(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Return a cleaned copy of the dataframe."""
        cleaned = dataframe.copy()
        cleaned = cleaned.dropna(how="all")
        cleaned = self._trim_and_collapse_whitespace(cleaned)

        if "Email" in cleaned.columns:
            cleaned["Email"] = cleaned["Email"].astype("string").str.strip().str.lower()

        if "Country" in cleaned.columns:
            cleaned["Country"] = self._country_normalizer.normalize_series(cleaned["Country"])

        return cleaned.reset_index(drop=True)

    @staticmethod
    def _trim_and_collapse_whitespace(dataframe: pd.DataFrame) -> pd.DataFrame:
        """Trim leading/trailing spaces and collapse repeated whitespace in string columns."""
        cleaned = dataframe.copy()
        string_columns = cleaned.select_dtypes(include=["object", "string"]).columns
        for column in string_columns:
            cleaned[column] = (
                cleaned[column]
                .astype("string")
                .str.strip()
                .str.replace(re.compile(r"\s+"), " ", regex=True)
            )
        return cleaned
