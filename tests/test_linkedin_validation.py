"""Tests for candidate LinkedIn validation."""

from services.candidate_assets.linkedinAssetValidator import LinkedInAssetValidator


def test_linkedin_profile_validation_accepts_in_and_pub_urls() -> None:
    """LinkedIn validator should accept public profile formats."""
    validator = LinkedInAssetValidator()

    assert validator.validate("linkedin.com/in/jane?trk=abc") == ("https://linkedin.com/in/jane", "valid")
    assert validator.validate("https://www.linkedin.com/pub/jane%20smith") == (
        "https://linkedin.com/pub/jane%20smith",
        "valid",
    )


def test_linkedin_profile_validation_rejects_company_page() -> None:
    """LinkedIn validator should reject non-profile formats."""
    url, status = LinkedInAssetValidator().validate("https://linkedin.com/company/acme")

    assert url == "https://linkedin.com/company/acme"
    assert status == "invalid"
