"""Subject line generation."""

from services.email_personalization.rule_loader import load_email_config


class SubjectLineGenerator:
    """Generate concise deterministic subject lines."""

    _type_labels = {
        "executive_problem": "executive problem hook",
        "executive_hook": "executive personalised hook",
        "hiring_manager_seek": "seeking opportunity",
        "seeker": "seeking opportunity",
        "observation_company": "observation + company",
        "hiring_signal": "hiring signal",
        "human_curiosity": "human curiosity",
        "fallback": "fallback",
    }

    def __init__(self) -> None:
        self._rules = load_email_config("subject_rules.json")

    def generate(self, subject_key: str, company: str, payload: dict | None = None) -> tuple[str, str]:
        """Return subject line and display subject type."""
        payload = payload or {}
        template = self._rules["formulas"].get(subject_key, self._rules["formulas"]["fallback"])

        # Extract placeholders
        candidate = payload.get("candidate", {})
        prospect = payload.get("prospect", {})
        key_skills = payload.get("key_skills") or []

        target_role = (
            candidate.get("target_role")
            or candidate.get("current_role")
            or prospect.get("role")
            or ""
        )
        role_skill = key_skills[0] if key_skills else target_role
        role_gap = key_skills[0] if key_skills else "workflow"

        subject = template.format(
            company=company or "your team",
            target_role=target_role,
            role_skill=role_skill,
            role_gap=role_gap,
        ).strip()

        subject = self._shorten(subject)
        return subject, self._type_labels.get(subject_key, "fallback")

    def _shorten(self, subject: str) -> str:
        """Keep subject under configured word limit."""
        max_words = int(self._rules.get("max_words", 10))
        words = subject.split()
        if len(words) <= max_words:
            return subject
        return " ".join(words[:max_words])
