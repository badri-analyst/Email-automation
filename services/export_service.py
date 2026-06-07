"""Export helpers for Streamlit download buttons."""

import pandas as pd


class ExportService:
    """Serialize processed dataframes for download."""

    @staticmethod
    def to_csv_bytes(dataframe: pd.DataFrame) -> bytes:
        """Return a UTF-8 CSV byte payload."""
        return dataframe.to_csv(index=False).encode("utf-8")
