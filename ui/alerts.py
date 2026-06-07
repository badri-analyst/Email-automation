"""Alert UI components."""

import streamlit as st


def render_success(message: str) -> None:
    """Render a success alert."""
    st.success(message)


def render_error(message: str) -> None:
    """Render an error alert."""
    st.error(message)


def render_warning(message: str) -> None:
    """Render a warning alert."""
    st.warning(message)
