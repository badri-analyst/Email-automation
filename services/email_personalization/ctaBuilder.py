"""CTA builder and validator."""


class CtaBuilder:
    """Build exactly one low-friction CTA."""

    _allowed = {
        "recruiter": ("resume review", "Would a quick resume review be useful?"),
        "hiring_manager": ("quick look", "Would a quick look be useful?"),
        "direct": ("short reply", "Would a short reply be easiest?"),
        "ideas": ("permission to send ideas", "Would it be useful if I sent a few role-relevant ideas?"),
        "fit": ("fit check", "Would a quick fit check make sense?"),
    }

    def build(self, variant: str = "recruiter") -> tuple[str, str]:
        """Return CTA type and sentence."""
        return self._allowed.get(variant, self._allowed["recruiter"])

    def is_valid_single_cta(self, email_body: str) -> bool:
        """Return True when the body contains one question mark or fewer."""
        return email_body.count("?") <= 1
