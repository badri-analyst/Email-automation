"""Tests for role-country status assignment."""

from services.role_country.roleCountryStatusService import RoleCountryStatusService


def test_status_assignment_role_missing() -> None:
    """Missing role should produce role_missing."""
    status, _ = RoleCountryStatusService().assign(False, False, True, True, False, False)

    assert status == "role_missing"


def test_status_assignment_role_only() -> None:
    """Missing country should produce role-only status."""
    status, _ = RoleCountryStatusService().assign(True, True, False, False, False, False)

    assert status == "role_only_intelligence_used"


def test_status_assignment_ready() -> None:
    """Supported role and country should be ready."""
    status, _ = RoleCountryStatusService().assign(True, True, True, True, False, False)

    assert status == "ready_for_personalization"
