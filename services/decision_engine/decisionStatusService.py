"""Decision status assignment service."""


class DecisionStatusService:
    """Assign final deterministic decision status and next action."""

    def assign(
        self,
        eligible: bool,
        eligibility_status: str,
        send_permission: str,
        selected_path: str,
        manual_review: bool,
    ) -> tuple[str, str, str]:
        """Return decision status, next action, and reason."""
        if not eligible:
            if eligibility_status == "skipped_duplicate":
                return "skipped_duplicate", "skip_duplicate", "Duplicate row was skipped."
            return "blocked_invalid_email", "skip_sending", "Email eligibility failed."
        if manual_review:
            return "manual_review_required", "manual_review", "Manual review is required before personalization or sending."
        if selected_path == "insufficient_data":
            return "insufficient_data", "manual_review", "Insufficient supported data for personalization."
        if selected_path == "company_fallback":
            return "company_fallback_selected", "generate_draft", "Company fallback was selected."
        if selected_path == "role_country_only":
            return "role_country_only_selected", "run_role_country_only_personalization", "Role-country-only path was selected."
        if send_permission == "blocked":
            return "gmail_not_configured", "generate_draft", "Sending is blocked; draft generation only."
        if send_permission == "draft_only":
            return "ready_for_draft_generation", "generate_draft", "Draft generation is allowed."
        if send_permission == "allowed":
            return "ready_for_sending", "send_email", "All send gates passed."
        return "ready_for_email_personalization", "generate_email", "Ready for email personalization."
