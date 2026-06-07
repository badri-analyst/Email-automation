"""Domain-specific exceptions."""


class SpreadsheetAppError(Exception):
    """Base application exception."""


class FileValidationError(SpreadsheetAppError):
    """Raised when an uploaded file is unsafe or unsupported."""


class SpreadsheetReadError(SpreadsheetAppError):
    """Raised when a spreadsheet cannot be parsed safely."""
