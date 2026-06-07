"""Map available personalization context to subject formula types."""


class SubjectSignalMapper:
    """Select a deterministic subject type from available context."""

    def select_subject_type(self, payload: dict) -> str:
        """Return subject formula key."""
        if payload.get("company_context", {}).get("growth_or_hiring_signal"):
            return "hiring_signal"
        if payload.get("linkedin_context"):
            return "human_curiosity"
        if payload.get("company_context"):
            return "observation_company"
        if payload.get("role_country_context"):
            return "executive_hook"
        return "fallback"

