"""Tests for role normalization."""

from services.role_country.roleNormalizationService import RoleNormalizationService


def test_role_normalization_uses_configured_aliases() -> None:
    """Role aliases should normalize deterministically."""
    service = RoleNormalizationService()

    assert service.normalize("BA") == "Business Analyst"
    assert service.normalize("IT BA") == "Business Analyst"
    assert service.normalize("PM") == "Project Manager"
