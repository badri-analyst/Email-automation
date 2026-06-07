"""Tests for company name normalization."""

from services.company_research.companyNameService import CompanyNameService


def test_company_name_normalization_removes_legal_suffixes_and_capitalizes() -> None:
    """Company names should remove legal suffixes while preserving originals elsewhere."""
    service = CompanyNameService()

    assert service.normalize("GOOGLE LLC") == "Google"
    assert service.normalize("Microsoft Corporation") == "Microsoft"
    assert service.normalize("Acme Pvt Ltd") == "Acme"
