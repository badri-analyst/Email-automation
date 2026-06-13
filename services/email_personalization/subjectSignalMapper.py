"""Map available personalization context to subject formula types."""

from services.email_personalization.rule_loader import load_email_config


class SubjectSignalMapper:
    """Select a deterministic subject type from available context."""

    def __init__(self) -> None:
        rules = load_email_config("subject_rules.json")
        self._exec_titles = [t.lower() for t in rules.get("executive_titles", [])]
        self._hiring_titles = [t.lower() for t in rules.get("hiring_manager_titles", [])]

    def _prospect_level(self, prospect_role: str) -> str:
        """Return 'executive', 'hiring_manager', or 'normal'."""
        role_lower = (prospect_role or "").lower()
        if any(t in role_lower for t in self._exec_titles):
            return "executive"
        if any(t in role_lower for t in self._hiring_titles):
            return "hiring_manager"
        return "normal"

    def select_subject_type(self, payload: dict) -> str:
        """Return subject formula key based on prospect seniority."""
        prospect_role = payload.get("prospect", {}).get("role", "")
        level = self._prospect_level(prospect_role)

        if level == "executive":
            # Use problem-solving / personalised hook for senior people
            if payload.get("opening_hook") or payload.get("tone_guidance"):
                return "executive_hook"
            return "executive_problem"

        if level == "hiring_manager":
            return "hiring_manager_seek"

        # Normal person / unknown — "Seeking <role> opportunity"
        return "seeker"
