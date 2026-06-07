"""Secure uploaded file handling and parsing."""

from collections.abc import Callable
from io import BytesIO
from pathlib import Path
from zipfile import BadZipFile

import pandas as pd
from charset_normalizer import from_bytes

from core.config import CONFIG, AppConfig
from core.exceptions import FileValidationError, SpreadsheetReadError
from models.schemas import ValidationErrorRecord


class FileService:
    """Read uploaded CSV and XLSX files without persisting them permanently."""

    def __init__(self, config: AppConfig = CONFIG) -> None:
        self._config = config

    def sanitize_filename(self, filename: str) -> str:
        """Return a basename-only filename stripped of unsafe path components."""
        return Path(filename).name.replace("\x00", "")

    def validate_upload(self, filename: str, size: int | None) -> str:
        """Validate upload name, extension, and size."""
        safe_name = self.sanitize_filename(filename)
        extension = Path(safe_name).suffix.casefold()

        if extension not in self._config.allowed_extensions:
            raise FileValidationError("Only .csv and .xlsx files are supported.")

        if size is not None and size > self._config.max_upload_size_bytes:
            raise FileValidationError(
                f"File exceeds the {self._config.max_upload_size_mb} MB upload limit."
            )

        return safe_name

    def read_uploaded_file(self, uploaded_file: object) -> tuple[pd.DataFrame, list[ValidationErrorRecord]]:
        """Read a Streamlit UploadedFile into a dataframe and return malformed-row warnings."""
        filename = getattr(uploaded_file, "name", "uploaded-file")
        size = getattr(uploaded_file, "size", None)
        safe_name = self.validate_upload(filename, size)
        payload = uploaded_file.getvalue()
        extension = Path(safe_name).suffix.casefold()

        if extension == ".csv":
            return self._read_csv(payload)
        if extension == ".xlsx":
            return self._read_xlsx(payload), []

        raise FileValidationError("Unsupported file extension.")

    def _read_csv(self, payload: bytes) -> tuple[pd.DataFrame, list[ValidationErrorRecord]]:
        """Read CSV bytes with best-effort encoding detection and malformed row capture."""
        encoding = self._detect_encoding(payload)
        malformed_rows: list[ValidationErrorRecord] = []

        def handle_bad_line(fields: list[str]) -> None:
            malformed_rows.append(
                ValidationErrorRecord(
                    category="Malformed Row",
                    invalid_value=",".join(fields),
                    reason="CSV row had an unexpected number of fields and was skipped",
                )
            )
            return None

        try:
            dataframe = pd.read_csv(
                BytesIO(payload),
                encoding=encoding,
                engine="python",
                on_bad_lines=self._bad_line_handler(handle_bad_line),
            )
        except UnicodeDecodeError as exc:
            raise SpreadsheetReadError("Could not decode CSV file with detected encoding.") from exc
        except pd.errors.EmptyDataError as exc:
            raise SpreadsheetReadError("CSV file is empty.") from exc
        except pd.errors.ParserError as exc:
            raise SpreadsheetReadError("CSV file could not be parsed safely.") from exc

        return dataframe, malformed_rows

    @staticmethod
    def _read_xlsx(payload: bytes) -> pd.DataFrame:
        """Read XLSX bytes using openpyxl through pandas."""
        try:
            return pd.read_excel(BytesIO(payload), engine="openpyxl")
        except BadZipFile as exc:
            raise SpreadsheetReadError("XLSX file is corrupted or not a valid spreadsheet.") from exc
        except ValueError as exc:
            raise SpreadsheetReadError("XLSX file has an invalid spreadsheet format.") from exc
        except Exception as exc:
            raise SpreadsheetReadError("XLSX file could not be read safely.") from exc

    @staticmethod
    def _detect_encoding(payload: bytes) -> str:
        """Detect CSV encoding, falling back to UTF-8."""
        match = from_bytes(payload).best()
        return match.encoding if match and match.encoding else "utf-8"

    @staticmethod
    def _bad_line_handler(callback: Callable[[list[str]], None]) -> Callable[[list[str]], None]:
        """Wrap pandas bad-line handling for testability."""
        return callback
