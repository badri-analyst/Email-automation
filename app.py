"""Streamlit entrypoint for the spreadsheet validation application."""

import streamlit as st

from core.config import CONFIG
from core.exceptions import FileValidationError, SpreadsheetReadError
from models.schemas import ProcessingResult, ValidationSummary
from services.cleaning_service import CleaningService
from services.export_service import ExportService
from services.file_service import FileService
from services.validation_service import ValidationService
from ui.alerts import render_error, render_success, render_warning
from ui.metrics import render_metrics
from ui.tables import render_cleaned_preview, render_paginated_dataframe
from ui.uploader import render_uploader
from utils.logger import get_logger

logger = get_logger(__name__)


def build_services() -> tuple[FileService, CleaningService, ValidationService, ExportService]:
    """Build application services."""
    return FileService(), CleaningService(), ValidationService(), ExportService()


def process_upload(uploaded_file: object) -> ProcessingResult:
    """Read, clean, and validate one uploaded spreadsheet."""
    file_service, cleaning_service, validation_service, _ = build_services()
    dataframe, malformed_rows = file_service.read_uploaded_file(uploaded_file)
    cleaned = cleaning_service.clean(dataframe)
    result = validation_service.validate(cleaned)
    result.malformed_rows.extend(malformed_rows)

    if result.summary and malformed_rows:
        malformed_count = len(malformed_rows)
        result.summary = ValidationSummary(
            total_rows=result.summary.total_rows,
            valid_rows=result.summary.valid_rows,
            invalid_rows=result.summary.invalid_rows + malformed_count,
            duplicate_rows=result.summary.duplicate_rows,
        )

    return result


def render_sidebar() -> None:
    """Render sidebar instructions."""
    st.sidebar.header("Instructions")
    st.sidebar.write("Upload a CSV or XLSX file containing Name, Email, Company, Role, and Country.")
    st.sidebar.write("The app cleans whitespace, normalizes countries, validates emails, and detects duplicates.")
    st.sidebar.write("Files are processed in memory and are not written to permanent storage.")


def render_downloads(result: ProcessingResult, export_service: ExportService) -> None:
    """Render export download buttons."""
    st.subheader("Exports")
    col_valid, col_duplicates, col_errors = st.columns(3)

    col_valid.download_button(
        "Download valid cleaned CSV",
        data=export_service.to_csv_bytes(result.valid_data),
        file_name="cleaned_valid_records.csv",
        mime="text/csv",
        disabled=result.valid_data.empty,
    )
    col_duplicates.download_button(
        "Download duplicate records CSV",
        data=export_service.to_csv_bytes(result.duplicate_data),
        file_name="duplicate_records.csv",
        mime="text/csv",
        disabled=result.duplicate_data.empty,
    )
    col_errors.download_button(
        "Download validation report CSV",
        data=export_service.to_csv_bytes(result.errors_dataframe),
        file_name="validation_report.csv",
        mime="text/csv",
        disabled=result.errors_dataframe.empty,
    )


def render_result(result: ProcessingResult) -> None:
    """Render processed validation result."""
    _, _, _, export_service = build_services()

    if result.summary:
        render_metrics(result.summary)

    if result.errors_dataframe.empty:
        render_success("Validation completed with no errors.")
    else:
        render_warning("Validation completed. Review the issues below before exporting.")

    render_cleaned_preview(result.cleaned_data)
    render_paginated_dataframe(result.errors_dataframe, "Validation Errors", "errors")
    render_paginated_dataframe(result.duplicate_data, "Duplicate Records", "duplicates")
    render_downloads(result, export_service)


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(page_title=CONFIG.app_name, layout="wide")
    st.title(CONFIG.app_name)
    render_sidebar()

    uploaded_file = render_uploader()
    if uploaded_file is None:
        st.info("Upload a CSV or XLSX file to begin.")
        return

    try:
        with st.spinner("Processing spreadsheet..."):
            result = process_upload(uploaded_file)
    except (FileValidationError, SpreadsheetReadError) as exc:
        logger.warning("Upload rejected: %s", exc)
        render_error(str(exc))
        return
    except Exception as exc:
        logger.exception("Unexpected processing error")
        render_error("The file could not be processed safely. Please check the format and try again.")
        return

    render_result(result)


if __name__ == "__main__":
    main()
