"""Gmail OAuth2 send-permission safety checks."""

from schemas.decisionSchema import CampaignSettings


class SendPermissionService:
    """Determine whether sending is allowed, draft-only, or blocked."""

    def evaluate(self, email_present: bool, settings: CampaignSettings) -> tuple[str, str]:
        """Return send permission and block reason."""
        if not email_present:
            if settings.allow_draft_when_email_missing:
                return "draft_only", "Email is missing; draft generation only."
            return "blocked", "Email is missing."
        if not settings.sending_enabled:
            return "draft_only", "Sending is disabled for this campaign."
        if not settings.gmail_configured:
            return "blocked", "Gmail OAuth2 is not configured."
        if not settings.gmail_valid:
            return "blocked", "Gmail OAuth2 configuration is invalid."
        return "allowed", ""
