"""Upload UI components."""

import streamlit as st

from core.config import CONFIG


def render_uploader() -> object | None:
    """Render the spreadsheet upload widget."""
    return st.file_uploader(
        "Upload spreadsheet",
        type=["csv", "xlsx"],
        accept_multiple_files=False,
        help=f"Maximum file size: {CONFIG.max_upload_size_mb} MB",
    )
