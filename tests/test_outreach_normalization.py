"""Tests for outreach normalization components."""

import pandas as pd

from services.normalization.column_alias_normalizer import ColumnAliasNormalizer
from services.normalization.company_normalizer import CompanyNormalizer
from services.normalization.country_normalizer import CountryNormalizer
from services.normalization.linkedin_normalizer import LinkedInNormalizer


def test_column_alias_normalization_is_configurable_and_deterministic() -> None:
    """Column aliases should normalize to deterministic outreach fields."""
    dataframe = pd.DataFrame(columns=["company_name", "linkedin profile", "Email Address"])

    normalized = ColumnAliasNormalizer().normalize_dataframe(dataframe)

    assert list(normalized.columns) == ["company", "linkedin_url", "email"]


def test_company_normalizer_removes_legal_suffixes() -> None:
    """Company normalizer should remove configured legal suffixes."""
    normalizer = CompanyNormalizer()

    assert normalizer.normalize("Google LLC") == "Google"
    assert normalizer.normalize("Microsoft Corporation") == "Microsoft"
    assert normalizer.normalize("Acme Pvt Ltd") == "Acme"


def test_country_normalizer_maps_common_aliases() -> None:
    """Country normalizer should map common aliases."""
    normalizer = CountryNormalizer()

    assert normalizer.normalize("USA") == "United States"
    assert normalizer.normalize("UK") == "United Kingdom"
    assert normalizer.normalize("UAE") == "United Arab Emirates"


def test_linkedin_normalizer_removes_tracking_and_standardizes_protocol() -> None:
    """LinkedIn normalizer should remove query tracking and standardize profile URLs."""
    normalizer = LinkedInNormalizer()

    assert normalizer.normalize("https://linkedin.com/in/john/?trk=abc") == "https://linkedin.com/in/john"
    assert normalizer.normalize("www.linkedin.com/in/jane%20doe?miniProfileUrn=abc") == (
        "https://linkedin.com/in/jane%20doe"
    )
