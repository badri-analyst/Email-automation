"""Tests for role-country country normalization."""

from services.role_country.countryNormalizationService import CountryNormalizationService


def test_country_normalization_uses_configured_aliases() -> None:
    """Country aliases should normalize deterministically."""
    service = CountryNormalizationService()

    assert service.normalize("US") == "United States"
    assert service.normalize("USA") == "United States"
    assert service.normalize("U.K.") == "United Kingdom"
    assert service.normalize("Britain") == "United Kingdom"
