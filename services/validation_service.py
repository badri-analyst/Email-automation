"""Enterprise validation workflow orchestration."""

import pandas as pd

from core.constants import NORMALIZED_REQUIRED_COLUMNS, REQUIRED_COLUMNS
from models.schemas import ProcessingResult, ValidationErrorRecord, ValidationSummary
from services.duplicate_service import DuplicateService
from utils.dataframe_utils import canonicalize_required_columns, normalize_column_name
from utils.email_utils import validate_email_address


class ValidationService:
    """Validate required fields, email format, and duplicates."""

    def __init__(self, duplicate_service: DuplicateService | None = None) -> None:
        self._duplicate_service = duplicate_service or DuplicateService()

    def canonicalize_columns(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Normalize required-column headers to canonical names."""
        normalized = dataframe.copy()
        normalized.columns = [str(column).strip() for column in normalized.columns]
        return canonicalize_required_columns(normalized, NORMALIZED_REQUIRED_COLUMNS)

    def validate_columns(self, dataframe: pd.DataFrame) -> list[ValidationErrorRecord]:
        """Validate required columns using trimmed, case-insensitive matching."""
        present = {normalize_column_name(column) for column in dataframe.columns}
        errors: list[ValidationErrorRecord] = []
        for required in REQUIRED_COLUMNS:
            if normalize_column_name(required) not in present:
                errors.append(
                    ValidationErrorRecord(
                        category="Missing Column",
                        column=required,
                        reason=f"Required column '{required}' is missing",
                    )
                )
        return errors

    def validate(self, dataframe: pd.DataFrame) -> ProcessingResult:
        """Run the complete validation workflow and return a processing result."""
        canonical = self.canonicalize_columns(dataframe)
        errors = self.validate_columns(canonical)

        if errors:
            empty = canonical.copy()
            summary = ValidationSummary(
                total_rows=len(canonical),
                valid_rows=0,
                invalid_rows=len(canonical),
                duplicate_rows=0,
            )
            return ProcessingResult(
                cleaned_data=canonical,
                valid_data=empty.iloc[0:0].copy(),
                duplicate_data=empty.iloc[0:0].copy(),
                validation_errors=errors,
                summary=summary,
            )

        row_invalid_mask = pd.Series(False, index=canonical.index)
        field_errors, required_invalid_mask = self._validate_required_values(canonical)
        email_errors, email_invalid_mask = self._validate_emails(canonical)
        row_invalid_mask = row_invalid_mask | required_invalid_mask | email_invalid_mask

        duplicate_marked = self._duplicate_service.mark_duplicates(canonical)
        duplicate_data = duplicate_marked[duplicate_marked["Is Duplicate"]].copy()
        duplicate_errors = self._duplicate_errors(duplicate_data)

        duplicate_mask = duplicate_marked["Is Duplicate"] if "Is Duplicate" in duplicate_marked else row_invalid_mask
        valid_data = duplicate_marked[~row_invalid_mask & ~duplicate_mask].drop(
            columns=["Is Duplicate", "Duplicate Reason"],
            errors="ignore",
        )

        all_errors = errors + field_errors + email_errors + duplicate_errors
        invalid_rows = set(error.row_number for error in all_errors if error.row_number is not None)
        summary = ValidationSummary(
            total_rows=len(canonical),
            valid_rows=len(valid_data),
            invalid_rows=len(invalid_rows),
            duplicate_rows=len(duplicate_data),
        )

        return ProcessingResult(
            cleaned_data=duplicate_marked,
            valid_data=valid_data,
            duplicate_data=duplicate_data,
            validation_errors=all_errors,
            summary=summary,
        )

    @staticmethod
    def _validate_required_values(dataframe: pd.DataFrame) -> tuple[list[ValidationErrorRecord], pd.Series]:
        """Validate required fields are not blank."""
        errors: list[ValidationErrorRecord] = []
        invalid_mask = pd.Series(False, index=dataframe.index)
        for column in REQUIRED_COLUMNS:
            values = dataframe[column].astype("string").str.strip()
            missing_mask = values.isna() | values.eq("")
            invalid_mask = invalid_mask | missing_mask
            for index, invalid_value in dataframe.loc[missing_mask, column].items():
                errors.append(
                    ValidationErrorRecord(
                        category="Missing Field",
                        row_number=int(index) + 2,
                        column=column,
                        invalid_value=invalid_value,
                        reason=f"Required field '{column}' is empty",
                    )
                )
        return errors, invalid_mask

    @staticmethod
    def _validate_emails(dataframe: pd.DataFrame) -> tuple[list[ValidationErrorRecord], pd.Series]:
        """Validate email addresses with the email-validator package."""
        errors: list[ValidationErrorRecord] = []
        invalid_mask = pd.Series(False, index=dataframe.index)

        for index, value in dataframe["Email"].items():
            is_valid, normalized, reason = validate_email_address(value)
            if is_valid:
                dataframe.at[index, "Email"] = normalized
                continue

            invalid_mask.at[index] = True
            errors.append(
                ValidationErrorRecord(
                    category="Invalid Email",
                    row_number=int(index) + 2,
                    column="Email",
                    invalid_value=value,
                    reason=reason or "Invalid email address",
                )
            )

        return errors, invalid_mask

    @staticmethod
    def _duplicate_errors(duplicate_data: pd.DataFrame) -> list[ValidationErrorRecord]:
        """Convert duplicate rows into validation error records."""
        errors: list[ValidationErrorRecord] = []
        if duplicate_data.empty:
            return errors

        for index, row in duplicate_data.iterrows():
            errors.append(
                ValidationErrorRecord(
                    category="Duplicate",
                    row_number=int(index) + 2,
                    column="Email/Name+Company",
                    invalid_value=row.get("Email"),
                    reason=str(row.get("Duplicate Reason", "Duplicate record")),
                )
            )
        return errors
