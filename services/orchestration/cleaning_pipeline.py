"""Outreach cleaning pipeline orchestration."""

import re
from dataclasses import dataclass
from typing import Any

import pandas as pd

from models.schemas import CleaningErrorRecord, CleaningPipelineResult, OutreachRecord
from services.cleaning.html_cleaner import HtmlCleaner
from services.cleaning.punctuation_cleaner import PunctuationCleaner
from services.cleaning.unicode_cleaner import UnicodeCleaner
from services.cleaning.whitespace_cleaner import WhitespaceCleaner
from services.inference.department_inference import DepartmentInference
from services.inference.name_splitter import NameSplitter
from services.inference.seniority_inference import SeniorityInference
from services.normalization.column_alias_normalizer import ColumnAliasNormalizer
from services.normalization.company_normalizer import CompanyNormalizer
from services.normalization.country_normalizer import CountryNormalizer
from services.normalization.linkedin_normalizer import LinkedInNormalizer
from services.orchestration.row_router import RowRouter


@dataclass(frozen=True)
class CleaningPipelineServices:
    """Dependency bundle for the cleaning pipeline."""

    column_alias_normalizer: ColumnAliasNormalizer = ColumnAliasNormalizer()
    whitespace_cleaner: WhitespaceCleaner = WhitespaceCleaner()
    unicode_cleaner: UnicodeCleaner = UnicodeCleaner()
    html_cleaner: HtmlCleaner = HtmlCleaner()
    punctuation_cleaner: PunctuationCleaner = PunctuationCleaner()
    company_normalizer: CompanyNormalizer = CompanyNormalizer()
    country_normalizer: CountryNormalizer = CountryNormalizer()
    linkedin_normalizer: LinkedInNormalizer = LinkedInNormalizer()
    name_splitter: NameSplitter = NameSplitter()
    seniority_inference: SeniorityInference = SeniorityInference()
    department_inference: DepartmentInference = DepartmentInference()
    row_router: RowRouter = RowRouter()


class CleaningPipeline:
    """Orchestrate outreach cleaning without repeating upstream validation checks."""

    _acronym_pattern = re.compile(r"^[A-Z0-9&]{2,}$")

    def __init__(self, services: CleaningPipelineServices | None = None) -> None:
        self._services = services or CleaningPipelineServices()

    def clean_dataframe(self, dataframe: pd.DataFrame) -> CleaningPipelineResult:
        """Clean a batch of upstream-validated outreach records."""
        normalized_columns = self._services.column_alias_normalizer.normalize_dataframe(dataframe)
        records: list[OutreachRecord] = []
        errors: list[CleaningErrorRecord] = []

        for index, row in normalized_columns.iterrows():
            row_number = int(index) + 2
            try:
                records.append(self._clean_row(row, row_number))
            except Exception as exc:
                errors.append(CleaningErrorRecord(row_number=row_number, reason=str(exc)))
                records.append(self._failed_record(row, "failed"))

        return CleaningPipelineResult(records=records, errors=errors)

    def _clean_row(self, row: pd.Series, row_number: int) -> OutreachRecord:
        """Clean one row and isolate failures to this record."""
        validation_status = self._field(row, "validation_status")
        if not self._services.row_router.should_clean(validation_status):
            return self._skipped_record(row)

        original_name = self._field(row, "name")
        original_company = self._field(row, "company")
        original_email = self._field(row, "email")
        original_linkedin = self._field(row, "linkedin_url")
        original_role = self._field(row, "role")
        original_country = self._field(row, "country")

        full_name = self._standardize_person_name(self._clean_text(original_name))
        email = self._clean_text(original_email).lower()
        company_name = self._standardize_company_display(self._clean_text(original_company))
        normalized_company = self._services.company_normalizer.normalize(company_name)
        role_title = self._standardize_title(self._clean_text(original_role))
        country = self._standardize_title(self._clean_text(original_country))
        normalized_country = self._services.country_normalizer.normalize(country)
        linkedin_url = self._services.linkedin_normalizer.normalize(self._clean_text(original_linkedin))
        first_name, last_name = self._services.name_splitter.split(full_name)
        seniority = self._services.seniority_inference.infer(role_title)
        department = self._services.department_inference.infer(role_title)
        cleaning_status = self._cleaning_status(
            (full_name, email, company_name, role_title, country),
            row_number,
        )

        return OutreachRecord(
            original_name=original_name,
            original_company=original_company,
            original_email=original_email,
            original_linkedin_url=original_linkedin,
            original_role_title=original_role,
            original_country=original_country,
            full_name=full_name,
            first_name=first_name,
            last_name=last_name,
            email=email,
            linkedin_url=linkedin_url,
            company_name=company_name,
            normalized_company_name=normalized_company,
            role_title=role_title,
            seniority_level=seniority,
            department=department,
            country=country,
            normalized_country=normalized_country,
            validation_status=validation_status,
            cleaning_status=cleaning_status,
        )

    def _clean_text(self, value: object) -> str:
        """Apply unicode, HTML, whitespace, and punctuation cleanup in pipeline order."""
        text = self._services.whitespace_cleaner.clean(value)
        text = self._services.unicode_cleaner.clean(text)
        text = self._services.html_cleaner.clean(text)
        text = self._services.punctuation_cleaner.clean(text)
        return self._services.whitespace_cleaner.clean(text)

    def _standardize_person_name(self, value: str) -> str:
        """Normalize person-name capitalization while preserving acronyms."""
        return " ".join(self._standardize_token(token) for token in value.split())

    def _standardize_company_display(self, value: str) -> str:
        """Normalize company display text before legal-suffix removal."""
        return " ".join(self._standardize_token(token) for token in value.split())

    def _standardize_title(self, value: str) -> str:
        """Normalize role and country display capitalization conservatively."""
        return " ".join(self._standardize_token(token) for token in value.split())

    def _standardize_token(self, token: str) -> str:
        """Title-case ordinary tokens while preserving intentional acronyms."""
        if self._acronym_pattern.match(token):
            return token
        if "-" in token:
            return "-".join(self._standardize_token(part) for part in token.split("-"))
        if "'" in token:
            return "'".join(self._standardize_token(part) for part in token.split("'"))
        return token.capitalize()

    @staticmethod
    def _field(row: pd.Series, field_name: str) -> str:
        """Safely read one canonical row field."""
        value: Any = row.get(field_name, "")
        if pd.isna(value):
            return ""
        return str(value)

    @staticmethod
    def _cleaning_status(required_values: tuple[str, ...], row_number: int) -> str:
        """Return a deterministic cleaning status."""
        if row_number < 0:
            return "failed"
        return "cleaned" if all(required_values) else "partially_cleaned"

    def _skipped_record(self, row: pd.Series) -> OutreachRecord:
        """Return an unchanged skipped output record for upstream-invalid rows."""
        return self._failed_record(row, "skipped")

    def _failed_record(self, row: pd.Series, status: str) -> OutreachRecord:
        """Return a structurally complete failed or skipped record."""
        original_name = self._field(row, "name")
        original_company = self._field(row, "company")
        original_email = self._field(row, "email")
        original_linkedin = self._field(row, "linkedin_url")
        original_role = self._field(row, "role")
        original_country = self._field(row, "country")
        validation_status = self._field(row, "validation_status")
        first_name, last_name = self._services.name_splitter.split(original_name)

        return OutreachRecord(
            original_name=original_name,
            original_company=original_company,
            original_email=original_email,
            original_linkedin_url=original_linkedin,
            original_role_title=original_role,
            original_country=original_country,
            full_name=original_name,
            first_name=first_name,
            last_name=last_name,
            email=original_email,
            linkedin_url=original_linkedin,
            company_name=original_company,
            normalized_company_name=original_company,
            role_title=original_role,
            seniority_level="unknown",
            department="unknown",
            country=original_country,
            normalized_country=original_country,
            validation_status=validation_status,
            cleaning_status=status,
        )
