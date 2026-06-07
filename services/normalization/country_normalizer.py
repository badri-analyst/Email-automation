"""Country normalization for outreach records."""

from collections.abc import Mapping

from core.constants import COUNTRY_NORMALIZATION_MAP
from utils.dataframe_utils import normalize_column_name


class CountryNormalizer:
    """Normalize country aliases through a configurable mapping."""

    def __init__(self, country_mapping: Mapping[str, str] | None = None) -> None:
        self._country_mapping = {
            normalize_column_name(alias): canonical
            for alias, canonical in (country_mapping or COUNTRY_NORMALIZATION_MAP).items()
        }

    def normalize(self, value: object) -> str:
        """Return the canonical country name where a mapping exists."""
        if value is None:
            return ""

        text = str(value).strip()
        if not text:
            return ""

        return self._country_mapping.get(normalize_column_name(text), text)

