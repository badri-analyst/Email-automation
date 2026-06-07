"""Tests for data cleaning and country normalization."""

import pandas as pd

from services.cleaning_service import CleaningService
from services.normalization_service import CountryNormalizationService


def test_cleaning_pipeline_trims_collapses_email_and_removes_empty_rows() -> None:
    """Cleaning should normalize strings, emails, countries, and empty rows."""
    dataframe = pd.DataFrame(
        [
            {
                "Name": "  Jane   Doe ",
                "Email": " JANE@Example.COM ",
                "Company": " Acme  Inc ",
                "Role": " VP  Sales ",
                "Country": " USA ",
            },
            {"Name": None, "Email": None, "Company": None, "Role": None, "Country": None},
        ]
    )

    cleaned = CleaningService().clean(dataframe)

    assert len(cleaned) == 1
    assert cleaned.loc[0, "Name"] == "Jane Doe"
    assert cleaned.loc[0, "Email"] == "jane@example.com"
    assert cleaned.loc[0, "Company"] == "Acme Inc"
    assert cleaned.loc[0, "Country"] == "United States"


def test_country_normalization_service_maps_common_variations() -> None:
    """Country normalization should standardize common aliases."""
    service = CountryNormalizationService()

    assert service.normalize_country("UK") == "United Kingdom"
    assert service.normalize_country("UAE") == "United Arab Emirates"
    assert service.normalize_country("Canada") == "Canada"
