"""Tests for the outreach cleaning pipeline orchestration."""

import pandas as pd

from services.orchestration.cleaning_pipeline import CleaningPipeline


def test_cleaning_pipeline_outputs_ai_ready_records_and_preserves_originals() -> None:
    """Pipeline should clean, normalize, infer, and preserve original values."""
    dataframe = pd.DataFrame(
        [
            {
                "Full Name": "  joHN   smITh ",
                "Email Address": " JOHN.SMITH+OUTREACH@Example.COM ",
                "company_name": "Google LLC",
                "Job Title": "<div>Senior Software Engineer</div>",
                "Country": "USA",
                "LinkedIn Profile": "https://linkedin.com/in/john/?trk=abc",
                "Validation Status": "valid",
            }
        ]
    )

    result = CleaningPipeline().clean_dataframe(dataframe)
    record = result.records[0]

    assert record.original_name == "  joHN   smITh "
    assert record.full_name == "John Smith"
    assert record.first_name == "John"
    assert record.last_name == "Smith"
    assert record.email == "john.smith+outreach@example.com"
    assert record.company_name == "Google LLC"
    assert record.normalized_company_name == "Google"
    assert record.role_title == "Senior Software Engineer"
    assert record.seniority_level == "senior"
    assert record.department == "engineering"
    assert record.normalized_country == "United States"
    assert record.linkedin_url == "https://linkedin.com/in/john"
    assert record.cleaning_status == "cleaned"


def test_cleaning_pipeline_skips_upstream_invalid_rows() -> None:
    """Pipeline should skip rows already rejected by validation."""
    dataframe = pd.DataFrame(
        [
            {
                "Name": "bad row",
                "Email": "bad",
                "Company": "Bad LLC",
                "Role": "Sales",
                "Country": "USA",
                "Validation Status": "invalid",
            }
        ]
    )

    result = CleaningPipeline().clean_dataframe(dataframe)

    assert result.records[0].cleaning_status == "skipped"
    assert result.records[0].full_name == "bad row"
