"""Email validation helpers."""

from email_validator import EmailNotValidError, validate_email


def validate_email_address(value: object) -> tuple[bool, str | None, str | None]:
    """Validate one email value and return validity, normalized value, and error reason."""
    if value is None:
        return False, None, "Email is empty"

    email = str(value).strip().lower()
    if not email or email == "nan":
        return False, None, "Email is empty"

    try:
        result = validate_email(email, check_deliverability=False)
    except EmailNotValidError as exc:
        return False, email, str(exc)

    return True, result.normalized.lower(), None
