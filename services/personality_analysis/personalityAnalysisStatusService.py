"""Status assignment for professional communication analysis."""


class PersonalityAnalysisStatusService:
    """Assign deterministic analysis statuses."""

    def assign(
        self,
        blocked: bool,
        manual_review: bool,
        has_profile: bool,
        has_posts: bool,
        has_company: bool,
        has_any_signal: bool,
    ) -> tuple[str, str, str]:
        """Return status, reason, and source type."""
        if blocked:
            return "unsafe_analysis_blocked", "Unsafe or sensitive inference language was blocked.", "insufficient_data"
        if manual_review:
            return "manual_review_required", "Analysis may require manual review for safe wording.", "combined_professional_context"
        if has_posts and has_any_signal:
            return "linkedin_posts_analysis_used", "LinkedIn posts summary provided observable professional evidence.", "linkedin_posts_summary"
        if has_profile and has_any_signal:
            return "linkedin_profile_analysis_used", "LinkedIn profile summary provided observable professional evidence.", "linkedin_profile_summary"
        if has_company and has_any_signal:
            return "company_based_analysis_used", "Person-level content was weak; company context was used without individual inference.", "company_research_summary"
        if has_any_signal:
            return "ready_for_personalization", "Observable professional communication evidence is available.", "combined_professional_context"
        return "insufficient_data", "Insufficient data.", "insufficient_data"
