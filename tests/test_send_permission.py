"""Tests for send permission and SMTP safety."""

from schemas.decisionSchema import CampaignSettings
from services.decision_engine.sendPermissionService import SendPermissionService


def test_send_permission_blocks_missing_email_when_drafts_not_allowed() -> None:
    """Missing email should block when draft fallback is disabled."""
    permission, reason = SendPermissionService().evaluate(
        False,
        CampaignSettings(allow_draft_when_email_missing=False),
    )

    assert permission == "blocked"
    assert reason


def test_send_permission_draft_only_when_sending_disabled() -> None:
    """Disabled sending should still allow draft generation."""
    permission, reason = SendPermissionService().evaluate(True, CampaignSettings(sending_enabled=False))

    assert permission == "draft_only"
    assert "disabled" in reason


def test_send_permission_blocks_invalid_smtp() -> None:
    """Invalid SMTP configuration should block sending."""
    permission, reason = SendPermissionService().evaluate(
        True,
        CampaignSettings(sending_enabled=True, smtp_configured=True, smtp_valid=False),
    )

    assert permission == "blocked"
    assert "invalid" in reason


def test_send_permission_allows_when_all_gates_pass() -> None:
    """Sending should be allowed only when all gates pass."""
    permission, reason = SendPermissionService().evaluate(
        True,
        CampaignSettings(sending_enabled=True, smtp_configured=True, smtp_valid=True),
    )

    assert permission == "allowed"
    assert reason == ""
