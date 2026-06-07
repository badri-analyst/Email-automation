"""Row eligibility checks."""

from typing import Any


class RowEligibilityService:
    """Evaluate email and duplicate eligibility from cleaned/validated output."""

    def evaluate(self, cleaning_output: dict[str, Any]) -> tuple[bool, str, str]:
        """Return eligibility flag, blocking status, and reason."""
        email = str(cleaning_output.get("email", cleaning_output.get("Email", ""))).strip()
        validation_status = str(cleaning_output.get("validation_status", "")).casefold()
        duplicate = bool(cleaning_output.get("is_duplicate", cleaning_output.get("Is Duplicate", False)))

        if duplicate:
            return False, "skipped_duplicate", "Duplicate row was confirmed and skipped."
        if not email:
            return False, "blocked_invalid_email", "Email is missing."
        if validation_status in {"invalid", "invalid_email", "blocked_invalid_email"}:
            return False, "blocked_invalid_email", "Email validation failed upstream."
        return True, "", ""
