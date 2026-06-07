"""Table rendering components."""

import math

import pandas as pd
import streamlit as st

from core.config import CONFIG


def render_paginated_dataframe(
    dataframe: pd.DataFrame,
    title: str,
    key_prefix: str,
    page_size: int = CONFIG.preview_page_size,
) -> None:
    """Render a scrollable dataframe with simple pagination controls."""
    st.subheader(title)
    if dataframe.empty:
        st.info("No records to display.")
        return

    total_pages = max(1, math.ceil(len(dataframe) / page_size))
    page = st.number_input(
        "Page",
        min_value=1,
        max_value=total_pages,
        value=1,
        step=1,
        key=f"{key_prefix}_page",
    )
    start = (int(page) - 1) * page_size
    end = start + page_size
    st.caption(f"Showing rows {start + 1:,}-{min(end, len(dataframe)):,} of {len(dataframe):,}")
    st.dataframe(dataframe.iloc[start:end], use_container_width=True, height=420)


def render_cleaned_preview(
    dataframe: pd.DataFrame,
    page_size: int = CONFIG.preview_page_size,
) -> None:
    """Render cleaned preview with pagination and duplicate-row highlighting."""
    st.subheader("Cleaned Preview")
    if dataframe.empty:
        st.info("No records to display.")
        return

    total_pages = max(1, math.ceil(len(dataframe) / page_size))
    page = st.number_input(
        "Preview page",
        min_value=1,
        max_value=total_pages,
        value=1,
        step=1,
        key="cleaned_preview_page",
    )
    start = (int(page) - 1) * page_size
    end = start + page_size
    page_data = dataframe.iloc[start:end]
    st.caption(f"Showing rows {start + 1:,}-{min(end, len(dataframe)):,} of {len(dataframe):,}")

    if "Is Duplicate" not in page_data.columns:
        st.dataframe(page_data, use_container_width=True, height=420)
        return

    def highlight(row: pd.Series) -> list[str]:
        duplicate = bool(row.get("Is Duplicate", False))
        return ["background-color: #fff3cd" if duplicate else "" for _ in row]

    st.dataframe(page_data.style.apply(highlight, axis=1), use_container_width=True, height=420)
