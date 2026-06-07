"""Metric UI components."""

import streamlit as st

from models.schemas import ValidationSummary


def render_metrics(summary: ValidationSummary) -> None:
    """Render validation summary metrics."""
    col_total, col_valid, col_invalid, col_duplicates = st.columns(4)
    col_total.metric("Total rows", f"{summary.total_rows:,}")
    col_valid.metric("Valid rows", f"{summary.valid_rows:,}")
    col_invalid.metric("Invalid rows", f"{summary.invalid_rows:,}")
    col_duplicates.metric("Duplicate rows", f"{summary.duplicate_rows:,}")
