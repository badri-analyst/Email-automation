"""DataFrame helper functions."""

import re

import pandas as pd


def normalize_column_name(column_name: object) -> str:
    """Normalize a column name for case-insensitive matching."""
    return re.sub(r"\s+", " ", str(column_name).strip()).casefold()


def canonicalize_required_columns(
    dataframe: pd.DataFrame,
    normalized_required_columns: dict[str, str],
) -> pd.DataFrame:
    """Rename required columns to canonical names while preserving extra columns."""
    rename_map: dict[str, str] = {}
    seen_targets: set[str] = set()

    for column in dataframe.columns:
        normalized = normalize_column_name(column)
        canonical = normalized_required_columns.get(normalized)
        if canonical and canonical not in seen_targets:
            rename_map[column] = canonical
            seen_targets.add(canonical)

    return dataframe.rename(columns=rename_map)


def row_numbers_for_mask(mask: pd.Series) -> list[int]:
    """Convert a boolean mask to human-readable spreadsheet row numbers."""
    return (mask[mask].index.to_series().astype(int) + 2).tolist()
