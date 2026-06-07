"""Subject line generation."""

from services.email_personalization.rule_loader import load_email_config


class SubjectLineGenerator:
    """Generate concise deterministic subject lines."""

    _type_labels = {
        "observation_company": "observation + company",
        "reverse_psychology": "reverse psychology",
        "hiring_signal": "hiring signal",
        "human_curiosity": "human curiosity",
        "executive_hook": "executive hook",
        "soft_fomo": "soft FOMO",
        "fallback": "fallback",
    }

    def __init__(self) -> None:
        self._rules = load_email_config("subject_rules.json")

    def generate(self, subject_key: str, company: str) -> tuple[str, str]:
        """Return subject line and display subject type."""
        template = self._rules["formulas"].get(subject_key, self._rules["formulas"]["fallback"])
        subject = template.format(company=company or "your team").strip()
        subject = self._shorten(subject)
        return subject, self._type_labels.get(subject_key, "fallback")

    def _shorten(self, subject: str) -> str:
        """Keep subject under configured word limit."""
        max_words = int(self._rules.get("max_words", 8))
        words = subject.split()
        if len(words) <= max_words:
            return subject
        return " ".join(words[:max_words])
