"""Duplicate detection services."""

import pandas as pd


class DuplicateService:
    """Detect duplicate business records efficiently."""

    def mark_duplicates(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Return duplicate records marked by email or Name+Company combination."""
        if dataframe.empty:
            return dataframe.copy()

        marked = dataframe.copy()
        duplicate_email = self._duplicate_mask(marked, ["Email"])
        duplicate_name_company = self._duplicate_mask(marked, ["Name", "Company"])

        marked["Is Duplicate"] = duplicate_email | duplicate_name_company
        marked["Duplicate Reason"] = ""
        marked.loc[duplicate_email, "Duplicate Reason"] = "Duplicate Email"
        marked.loc[duplicate_name_company, "Duplicate Reason"] = marked.loc[
            duplicate_name_company, "Duplicate Reason"
        ].where(
            marked.loc[duplicate_name_company, "Duplicate Reason"].eq(""),
            marked.loc[duplicate_name_company, "Duplicate Reason"] + "; ",
        ) + "Duplicate Name + Company"

        return marked

    def get_duplicates(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Return only rows marked as duplicates."""
        marked = self.mark_duplicates(dataframe)
        if "Is Duplicate" not in marked.columns:
            return marked
        return marked[marked["Is Duplicate"]].copy()

    @staticmethod
    def _duplicate_mask(dataframe: pd.DataFrame, subset: list[str]) -> pd.Series:
        """Build a duplicate mask for columns present in the dataframe."""
        if any(column not in dataframe.columns for column in subset):
            return pd.Series(False, index=dataframe.index)

        normalized = dataframe[subset].astype("string").apply(lambda col: col.str.strip().str.casefold())
        complete = normalized.notna().all(axis=1) & normalized.ne("").all(axis=1)
        return normalized.duplicated(keep=False) & complete
