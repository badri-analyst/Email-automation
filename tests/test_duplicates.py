"""Tests for duplicate detection."""

import pandas as pd

from services.duplicate_service import DuplicateService


def test_duplicate_detection_marks_duplicate_email_and_name_company() -> None:
    """Duplicate service should mark duplicate emails and Name+Company pairs."""
    dataframe = pd.DataFrame(
        [
            {"Name": "Jane", "Email": "jane@example.com", "Company": "Acme"},
            {"Name": "John", "Email": "jane@example.com", "Company": "Other"},
            {"Name": "Sam", "Email": "sam@example.com", "Company": "Acme"},
            {"Name": "Sam", "Email": "sam2@example.com", "Company": "Acme"},
        ]
    )

    marked = DuplicateService().mark_duplicates(dataframe)

    assert marked["Is Duplicate"].tolist() == [True, True, True, True]
    assert "Duplicate Email" in marked.loc[0, "Duplicate Reason"]
    assert "Duplicate Name + Company" in marked.loc[2, "Duplicate Reason"]


def test_duplicate_detection_ignores_blank_duplicate_keys() -> None:
    """Blank duplicate keys should not be treated as duplicates."""
    dataframe = pd.DataFrame(
        [
            {"Name": "", "Email": "", "Company": ""},
            {"Name": "", "Email": "", "Company": ""},
        ]
    )

    marked = DuplicateService().mark_duplicates(dataframe)

    assert marked["Is Duplicate"].tolist() == [False, False]
