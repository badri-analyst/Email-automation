"""Column alias normalization service."""

from collections.abc import Mapping

import pandas as pd

from core.constants import OUTREACH_COLUMN_ALIAS_MAP
from utils.dataframe_utils import normalize_column_name


class ColumnAliasNormalizer:
    """Normalize source columns to deterministic outreach field names."""

    def __init__(self, alias_mapping: Mapping[str, str] | None = None) -> None:
        self._alias_mapping = {
            normalize_column_name(alias): canonical
            for alias, canonical in (alias_mapping or OUTREACH_COLUMN_ALIAS_MAP).items()
        }

    def normalize_dataframe(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Return a dataframe with configured aliases renamed to canonical fields."""
        rename_map: dict[object, str] = {}
        used_targets: set[str] = set()

        for column in dataframe.columns:
            alias_key = normalize_column_name(column)
            target = self._alias_mapping.get(alias_key)
            if target and target not in used_targets:
                rename_map[column] = target
                used_targets.add(target)

        return dataframe.rename(columns=rename_map)

