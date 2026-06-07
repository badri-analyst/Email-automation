"""Typed domain models for validation and processing results."""

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class ValidationErrorRecord:
    """A validation issue isolated to a row, column, or file-level check."""

    category: str
    reason: str
    row_number: int | None = None
    column: str | None = None
    invalid_value: Any | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert the validation error to a serializable dictionary."""
        return {
            "category": self.category,
            "row_number": self.row_number,
            "column": self.column,
            "invalid_value": self.invalid_value,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ValidationSummary:
    """Aggregate validation counters for UI metrics and reports."""

    total_rows: int
    valid_rows: int
    invalid_rows: int
    duplicate_rows: int


@dataclass
class ProcessingResult:
    """Complete result returned by the processing pipeline."""

    cleaned_data: pd.DataFrame
    valid_data: pd.DataFrame
    duplicate_data: pd.DataFrame
    validation_errors: list[ValidationErrorRecord] = field(default_factory=list)
    malformed_rows: list[ValidationErrorRecord] = field(default_factory=list)
    summary: ValidationSummary | None = None

    @property
    def errors_dataframe(self) -> pd.DataFrame:
        """Return validation and malformed-row errors as a dataframe."""
        records = [error.to_dict() for error in self.validation_errors + self.malformed_rows]
        return pd.DataFrame.from_records(
            records,
            columns=["category", "row_number", "column", "invalid_value", "reason"],
        )


@dataclass(frozen=True)
class OutreachRecord:
    """Deterministic AI-ready outreach record produced by the cleaning pipeline."""

    original_name: str
    original_company: str
    original_email: str
    original_linkedin_url: str
    original_role_title: str
    original_country: str
    full_name: str
    first_name: str
    last_name: str
    email: str
    linkedin_url: str
    company_name: str
    normalized_company_name: str
    role_title: str
    seniority_level: str
    department: str
    country: str
    normalized_country: str
    validation_status: str
    cleaning_status: str

    def to_dict(self) -> dict[str, str]:
        """Return the outreach record as a serializable dictionary."""
        return {
            "original_name": self.original_name,
            "original_company": self.original_company,
            "original_email": self.original_email,
            "original_linkedin_url": self.original_linkedin_url,
            "original_role_title": self.original_role_title,
            "original_country": self.original_country,
            "full_name": self.full_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "linkedin_url": self.linkedin_url,
            "company_name": self.company_name,
            "normalized_company_name": self.normalized_company_name,
            "role_title": self.role_title,
            "seniority_level": self.seniority_level,
            "department": self.department,
            "country": self.country,
            "normalized_country": self.normalized_country,
            "validation_status": self.validation_status,
            "cleaning_status": self.cleaning_status,
        }


@dataclass(frozen=True)
class CleaningErrorRecord:
    """Row-isolated cleaning failure record."""

    row_number: int
    reason: str
    field: str | None = None

    def to_dict(self) -> dict[str, str | int | None]:
        """Return the error as a serializable dictionary."""
        return {"row_number": self.row_number, "field": self.field, "reason": self.reason}


@dataclass(frozen=True)
class CleaningPipelineResult:
    """Batch output from the outreach cleaning pipeline."""

    records: list[OutreachRecord]
    errors: list[CleaningErrorRecord] = field(default_factory=list)

    @property
    def dataframe(self) -> pd.DataFrame:
        """Return cleaned outreach records as a dataframe."""
        return pd.DataFrame.from_records([record.to_dict() for record in self.records])

    @property
    def errors_dataframe(self) -> pd.DataFrame:
        """Return row-isolated cleaning errors as a dataframe."""
        return pd.DataFrame.from_records([error.to_dict() for error in self.errors])
