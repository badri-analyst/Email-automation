"""Spreadsheet parsing for uploaded recruiter lead sheets."""

from __future__ import annotations

import base64
import io
import re
from typing import Any

import pandas as pd


COLUMN_ALIASES = {
    # ── NAME ──────────────────────────────────────────────────────────────
    "name": "name",
    "full name": "name",
    "full_name": "name",
    "fullname": "name",
    "candidate name": "name",
    "candidate_name": "name",
    "contact name": "name",
    "contact_name": "name",
    "person name": "name",
    "person_name": "name",
    "first name": "first_name",
    "first_name": "first_name",
    "firstname": "first_name",
    "given name": "first_name",
    "given_name": "first_name",
    "last name": "last_name",
    "last_name": "last_name",
    "lastname": "last_name",
    "surname": "last_name",
    "family name": "last_name",
    "family_name": "last_name",

    # ── EMAIL ─────────────────────────────────────────────────────────────
    "email": "email",
    "email address": "email",
    "email_address": "email",
    "emailaddress": "email",
    "e-mail": "email",
    "e_mail": "email",
    "mail": "email",
    "work email": "email",
    "work_email": "email",
    "workemail": "email",
    "work mail": "email",
    "work_mail": "email",
    "business email": "email",
    "business_email": "email",
    "company email": "email",
    "company_email": "email",
    "corporate email": "email",
    "corporate_email": "email",
    "contact email": "email",
    "contact_email": "email",
    "professional email": "email",
    "professional_email": "email",
    "email id": "email",
    "email_id": "email",
    "emailid": "email",

    # ── COMPANY ───────────────────────────────────────────────────────────
    "company": "company",
    "company name": "company",
    "company_name": "company",
    "companyname": "company",
    "organization": "company",
    "organisation": "company",
    "org": "company",
    "employer": "company",
    "current company": "company",
    "current_company": "company",
    "workplace": "company",
    "firm": "company",
    "business": "company",
    "account": "company",
    "account name": "company",
    "account_name": "company",

    # ── ROLE / JOB TITLE ─────────────────────────────────────────────────
    "role": "role",
    "job title": "role",
    "job_title": "role",
    "jobtitle": "role",
    "title": "role",
    "position": "role",
    "designation": "role",
    "job role": "role",
    "job_role": "role",
    "current role": "role",
    "current_role": "role",
    "current title": "role",
    "current_title": "role",
    "current position": "role",
    "current_position": "role",
    "function": "role",
    "occupation": "role",

    # ── COUNTRY / LOCATION ───────────────────────────────────────────────
    "country": "country",
    "location": "country",
    "region": "country",
    "geography": "country",
    "geo": "country",
    "city": "country",
    "state": "country",
    "country/region": "country",
    "country_region": "country",

    # ── LINKEDIN ─────────────────────────────────────────────────────────
    "linkedin": "linkedin_url",
    "linkedin url": "linkedin_url",
    "linkedin_url": "linkedin_url",
    "linkedin profile": "linkedin_url",
    "linkedin_profile": "linkedin_url",
    "linkedin profile url": "linkedin_url",
    "linkedin_profile_url": "linkedin_url",
    "linkedin link": "linkedin_url",
    "linkedin_link": "linkedin_url",
    "li url": "linkedin_url",
    "li_url": "linkedin_url",
    "social": "linkedin_url",
    "social url": "linkedin_url",
    "profile url": "linkedin_url",
    "profile_url": "linkedin_url",

    # ── COMPANY WEBSITE ──────────────────────────────────────────────────
    "website": "company_website",
    "company website": "company_website",
    "company_website": "company_website",
    "domain": "company_website",
    "url": "company_website",
    "company url": "company_website",
    "company_url": "company_website",
    "web": "company_website",
    "site": "company_website",
    "homepage": "company_website",
}

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _normalize_header(value: Any) -> str:
    # Strip, lowercase, collapse whitespace and underscores for matching
    text = re.sub(r"[\s_]+", " ", str(value or "")).strip().lower()
    return COLUMN_ALIASES.get(text, re.sub(r"\s+", "_", text))


def _clean_cell(value: Any) -> str:
    try:
        if pd.isna(value):
            return ""
    except (ValueError, TypeError):
        pass
    return re.sub(r"\s+", " ", str(value)).strip()


def _read_dataframe(filename: str, content: bytes) -> pd.DataFrame:
    lower_name = filename.lower()
    if lower_name.endswith(".xlsx"):
        return pd.read_excel(io.BytesIO(content), engine="openpyxl", dtype=str)
    if lower_name.endswith(".csv"):
        for encoding in ("utf-8-sig", "utf-8", "latin1"):
            try:
                return pd.read_csv(
                    io.BytesIO(content),
                    dtype=str,
                    encoding=encoding,
                    on_bad_lines="skip",
                )
            except UnicodeDecodeError:
                continue
        return pd.read_csv(io.BytesIO(content), dtype=str, encoding="latin1", on_bad_lines="skip")
    raise ValueError("Unsupported spreadsheet format. Upload a CSV or XLSX file.")


def _merge_first_last_name(dataframe: pd.DataFrame) -> pd.DataFrame:
    """If no 'name' column but first_name / last_name exist, combine them."""
    if "name" not in dataframe.columns:
        has_first = "first_name" in dataframe.columns
        has_last = "last_name" in dataframe.columns
        if has_first or has_last:
            first = dataframe.get("first_name", pd.Series("", index=dataframe.index)).fillna("")
            last = dataframe.get("last_name", pd.Series("", index=dataframe.index)).fillna("")
            dataframe["name"] = (first + " " + last).str.strip()
    return dataframe


def _find_email_column(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Last resort: scan column values to find one that looks like emails."""
    if "email" in dataframe.columns:
        return dataframe
    for col in dataframe.columns:
        sample = dataframe[col].dropna().astype(str).head(20)
        matches = sample.apply(lambda v: bool(EMAIL_PATTERN.match(v.strip().lower())))
        if matches.sum() >= max(1, len(sample) // 2):
            dataframe = dataframe.rename(columns={col: "email"})
            return dataframe
    raise ValueError(
        "No email column found. Make sure your spreadsheet has a column named "
        "'Email', 'Work Email', 'Email Address', or similar."
    )


def parse_spreadsheet(payload: dict[str, Any]) -> dict[str, Any]:
    filename = re.sub(r"[^\w.\- ]", "", payload.get("filename") or "uploaded_spreadsheet")
    encoded = payload.get("content_base64") or ""
    if not encoded:
        raise ValueError("Uploaded spreadsheet was empty.")

    content = base64.b64decode(encoded)
    dataframe = _read_dataframe(filename, content)
    dataframe = dataframe.dropna(how="all")
    dataframe.columns = [_normalize_header(column) for column in dataframe.columns]
    dataframe = _merge_first_last_name(dataframe)
    dataframe = _find_email_column(dataframe)

    rows: list[dict[str, Any]] = []
    validation_errors: list[dict[str, Any]] = []
    duplicate_indexes: set[int] = set()

    email_counts = dataframe.get("email", pd.Series(dtype=str)).fillna("").map(_clean_cell).str.lower().value_counts()
    combo_counts: dict[tuple[str, str], int] = {}
    for _, raw_row in dataframe.iterrows():
        name = _clean_cell(raw_row.get("name", "")).lower()
        company = _clean_cell(raw_row.get("company", "")).lower()
        if name or company:
            combo_counts[(name, company)] = combo_counts.get((name, company), 0) + 1

    for index, raw_row in dataframe.iterrows():
        row_number = int(index) + 2
        row = {
            "name": _clean_cell(raw_row.get("name", "")),
            "email": _clean_cell(raw_row.get("email", "")).lower(),
            "company": _clean_cell(raw_row.get("company", "")),
            "role": _clean_cell(raw_row.get("role", "")),
            "country": _clean_cell(raw_row.get("country", "")),
            "linkedin_url": _clean_cell(raw_row.get("linkedin_url", "")),
            "company_website": _clean_cell(raw_row.get("company_website", "")),
        }

        errors: list[str] = []
        if not row["name"]:
            errors.append("Missing name")
        if not row["email"]:
            errors.append("Missing email")
        elif not EMAIL_PATTERN.match(row["email"]):
            errors.append("Invalid email format")
        if not row["company"]:
            errors.append("Missing company")

        duplicate = False
        if row["email"] and email_counts.get(row["email"], 0) > 1:
            duplicate = True
        combo_key = (row["name"].lower(), row["company"].lower())
        if row["name"] and row["company"] and combo_counts.get(combo_key, 0) > 1:
            duplicate = True
        if duplicate:
            duplicate_indexes.add(index)

        row["validation_status"] = "invalid" if errors else "valid"
        row["validation_errors"] = errors
        rows.append(row)

        for reason in errors:
            validation_errors.append({
                "row_number": row_number,
                "invalid_value": row.get("email") or row.get("name") or "",
                "reason": reason,
            })

    valid_rows = sum(1 for row in rows if row["validation_status"] == "valid")
    invalid_rows = len(rows) - valid_rows

    return {
        "filename": filename,
        "rows": rows,
        "validation": {
            "total_rows": len(rows),
            "valid_rows": valid_rows,
            "invalid_rows": invalid_rows,
            "duplicate_rows": len(duplicate_indexes),
        },
        "validation_errors": validation_errors,
    }
