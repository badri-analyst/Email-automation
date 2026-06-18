"""Subject line generation."""

import hashlib

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
        formulas = self._rules["formulas"].get(subject_key, self._rules["formulas"]["fallback"])

        # Support both list and single string formulas
        if isinstance(formulas, list):
            # Pick deterministically based on company name so same company always gets same subject
            idx = int(hashlib.md5(company.encode()).hexdigest(), 16) % len(formulas)
            template = formulas[idx]
        else:
            template = formulas

        # Extract placeholders
        candidate = payload.get("candidate", {})
        prospect = payload.get("prospect", {})
        key_skills = payload.get("key_skills") or []
        company_context = payload.get("company_context", {})

        target_role = (
            candidate.get("target_role")
            or candidate.get("current_role")
            or prospect.get("role")
            or ""
        )
        role_skill = key_skills[0] if key_skills else target_role
        role_gap = key_skills[0] if key_skills else "workflow"

        # Extract short company signal from research for use in subject line
        company_signal = self._extract_company_signal(payload, company_context)

        subject = template.format(
            company=company or "your team",
            target_role=target_role,
            role_skill=role_skill,
            role_gap=role_gap,
            company_signal=company_signal or company,
        ).strip()

        subject = self._shorten(subject)
        return subject, self._type_labels.get(subject_key, "fallback")

    @staticmethod
    def _extract_company_signal(payload: dict, company_context: dict) -> str:
        """Extract a short company-specific signal for subject line use."""
        def valid(v):
            return v and str(v).strip() not in ("", "Insufficient data.")

        # Use opening hook — extract first few words
        hook = str(payload.get("opening_hook") or "").strip()
        if valid(hook):
            # Shorten to key phrase — strip common openers
            for prefix in ["I came across ", "I noticed ", "Congratulations on ", "Saw "]:
                if hook.lower().startswith(prefix.lower()):
                    hook = hook[len(prefix):]
                    break
            words = hook.split()
            return " ".join(words[:5]).rstrip(".,—-")

        # Fall back to growth signal
        if valid(company_context.get("growth_signal")):
            words = str(company_context["growth_signal"]).split()
            return " ".join(words[:5]).rstrip(".,—-")

        # Fall back to industry
        if valid(company_context.get("industry")):
            return str(company_context["industry"]).split(",")[0].strip()

        return ""

    def _shorten(self, subject: str) -> str:
        """Keep subject under configured word limit."""
        max_words = int(self._rules.get("max_words", 10))
        words = subject.split()
        if len(words) <= max_words:
            return subject
        return " ".join(words[:max_words])
