"""Application configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    """Immutable runtime settings for the Streamlit application."""

    app_name: str = "Spreadsheet Validation Workbench"
    max_upload_size_mb: int = 10
    preview_page_size: int = 100
    allowed_extensions: tuple[str, ...] = (".csv", ".xlsx")

    @property
    def max_upload_size_bytes(self) -> int:
        """Return the maximum upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024


CONFIG = AppConfig()
