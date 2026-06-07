"""Email draft safety filtering."""

import re

from services.email_personalization.rule_loader import load_email_config


class EmailSafetyFilter:
    """Block hallucinated, sensitive, manipulative, or score-like content."""

    def __init__(self) -> None:
        self._rules = load_email_config("forbidden_phrases.json")

    def check(self, subject: str, body: str) -> tuple[bool, str]:
        """Return whether content is safe and reason if blocked."""
        text = f"{subject} {body}".casefold()
        for group in ("hallucination_risks", "sensitive_assumptions", "manipulative_language", "score_fields"):
            for phrase in self._rules[group]:
                if phrase.casefold() in text:
                    return False, f"Blocked forbidden {group} phrase: {phrase}."
        if re.search(r"\b\d+%\b", text):
            return False, "Blocked unsupported percentage claim."
        return True, ""
