"""Research status assignment."""

from urllib.parse import urlsplit

from schemas.research_schema import ResearchInput


class ResearchStatusManager:
    """Assign deterministic research statuses without scoring."""

    def linkedin_status(self, linkedin_url: str) -> str | None:
        """Return a terminal LinkedIn URL status when applicable."""
        if not linkedin_url.strip():
            return "linkedin_missing"

        candidate = linkedin_url if "://" in linkedin_url else f"https://{linkedin_url}"
        parsed = urlsplit(candidate)
        host = parsed.netloc.casefold()
        path = parsed.path.rstrip("/")

        if host not in {"linkedin.com", "www.linkedin.com"} or not path.startswith("/in/"):
            return "linkedin_invalid"
        return None

    def assign(self, research_input: ResearchInput, person_evidence: str, company_evidence: str) -> tuple[str, str]:
        """Assign final status and reason from accessible evidence."""
        linkedin_issue = self.linkedin_status(research_input.linkedin_url)
        if linkedin_issue:
            return linkedin_issue, "LinkedIn URL is missing or not a public profile URL."

        if not research_input.linkedin_accessible:
            return "linkedin_inaccessible", "LinkedIn profile was marked inaccessible."

        if person_evidence:
            return "ready_for_personalization", "Sufficient professional profile evidence exists."

        if company_evidence:
            return "company_fallback_used", "Person-level evidence is weak; company evidence was used."

        return "insufficient_data", "Insufficient data."
