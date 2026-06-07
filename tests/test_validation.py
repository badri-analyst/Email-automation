"""Tests for validation workflows."""

import pandas as pd

from services.validation_service import ValidationService


def test_required_column_validation_is_case_insensitive_and_trims_headers() -> None:
    """Required columns should match despite case and whitespace differences."""
    dataframe = pd.DataFrame(
        columns=[" name ", "EMAIL", "Company", "role", " Country "],
        data=[["Jane", "jane@example.com", "Acme", "Manager", "USA"]],
    )

    service = ValidationService()
    canonical = service.canonicalize_columns(dataframe)
    errors = service.validate_columns(canonical)

    assert errors == []
    assert {"Name", "Email", "Company", "Role", "Country"}.issubset(canonical.columns)


def test_missing_required_column_generates_validation_error() -> None:
    """Missing required columns should produce file-level validation errors."""
    dataframe = pd.DataFrame(columns=["Name", "Email", "Company", "Country"])

    errors = ValidationService().validate_columns(dataframe)

    assert len(errors) == 1
    assert errors[0].category == "Missing Column"
    assert errors[0].column == "Role"


def test_invalid_email_includes_row_value_and_reason() -> None:
    """Invalid emails should include row number, invalid value, and reason."""
    dataframe = pd.DataFrame(
        [
            {
                "Name": "Jane",
                "Email": "not-an-email",
                "Company": "Acme",
                "Role": "Manager",
                "Country": "United States",
            }
        ]
    )

    result = ValidationService().validate(dataframe)
    email_errors = [error for error in result.validation_errors if error.category == "Invalid Email"]

    assert len(email_errors) == 1
    assert email_errors[0].row_number == 2
    assert email_errors[0].invalid_value == "not-an-email"
    assert email_errors[0].reason
    assert result.valid_data.empty
