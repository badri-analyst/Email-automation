"""Spreadsheet parsing for uploaded recruiter lead sheets."""

from __future__ import annotations

import base64
import io
import re
from typing import Any

import pandas as pd


COLUMN_ALIASES = {
    "name": "name",
    "full name": "name",
    "candidate name": "name",
    "contact name": "name",
    "email": "email",
    "email address": "email",
    "mail": "email",
    "company": "company",
    "company name": "company",
    "organization": "company",
    "organisation": "company",
    "org": "company",
    "role": "role",
    "job title": "role",
    "title": "role",
    "position": "role",
    "country": "country",
    "location": "country",
    "linkedin": "linkedin_url",
    "linkedin url": "linkedin_url",
    "linkedin profile": "linkedin_url",
    "linkedin profile url": "linkedin_url",
    "website": "company_website",
    "company website": "company_website",
    "domain": "company_website",
}

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _normalize_header(value: Any) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip().lower()
    return COLUMN_ALIASES.get(text, text.replace(" ", "_"))


def _clean_cell(value: Any) -> str:
    if pd.isna(value):
        return ""
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


def parse_spreadsheet(payload: dict[str, Any]) -> dict[str, Any]:
    filename = re.sub(r"[^\w.\- ]", "", payload.get("filename") or "uploaded_spreadsheet")
    encoded = payload.get("content_base64") or ""
    if not encoded:
        raise ValueError("Uploaded spreadsheet was empty.")

    content = base64.b64decode(encoded)
    dataframe = _read_dataframe(filename, content)
    dataframe = dataframe.dropna(how="all")
    dataframe.columns = [_normalize_header(column) for column in dataframe.columns]
    if "email" not in dataframe.columns:
        raise ValueError("No valid email column found in uploaded Excel sheet.")

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
