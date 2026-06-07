"""Company research status assignment."""

from schemas.companyResearchSchema import INSUFFICIENT_DATA, CompanyRecentUpdate


class CompanyResearchStatusService:
    """Assign deterministic company research statuses and reasons."""

    _fallback_trigger_statuses = {
        "insufficient_data",
        "company_fallback_used",
        "linkedin_missing",
        "linkedin_invalid",
        "linkedin_inaccessible",
        "research_failed",
    }

    def should_research(self, linkedin_research_status: str, enrichment_mode: bool) -> bool:
        """Return whether company research should run."""
        return enrichment_mode or linkedin_research_status in self._fallback_trigger_statuses

    def assign(
        self,
        website_status: str,
        overview: str,
        values_summary: str,
        updates: list[CompanyRecentUpdate],
        growth_signal: str,
        linkedin_research_status: str,
        manual_review_flag: bool,
    ) -> tuple[str, str]:
        """Return company research status and reason."""
        if manual_review_flag:
            return "manual_review_required", "Company data requires manual review."
        if website_status == "missing" and overview == INSUFFICIENT_DATA:
            return "company_website_missing", "No company website or approved company evidence was available."
        if updates:
            return "recent_news_found", "Recent company update evidence is available."
        if values_summary != INSUFFICIENT_DATA:
            return "company_values_found", "Company values evidence is available."
        if growth_signal != INSUFFICIENT_DATA:
            return "ready_for_personalization", "Growth or hiring signal evidence is available."
        if overview != INSUFFICIENT_DATA:
            if linkedin_research_status in self._fallback_trigger_statuses:
                return "company_fallback_used", "Company-level evidence was used as fallback context."
            return "company_basic_data_found", "Basic company evidence is available."
        return "insufficient_data", "Insufficient data."
