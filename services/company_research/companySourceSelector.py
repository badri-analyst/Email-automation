"""Company research source classification and selection."""

from schemas.companyResearchSchema import ApprovedCompanySource, CompanyResearchSourceType


class CompanySourceSelector:
    """Classify and choose approved company-level source snippets."""

    _priority: tuple[CompanyResearchSourceType, ...] = (
        "official_website",
        "careers_page",
        "linkedin_company_page",
        "company_news",
        "search_result",
        "email_domain",
    )

    def primary_source_type(self, sources: list[ApprovedCompanySource], website_status: str) -> CompanyResearchSourceType:
        """Return the strongest available source type."""
        for source_type in self._priority:
            if any(source.source_type == source_type and source.text for source in sources):
                return source_type
        if website_status == "inferred":
            return "email_domain"
        return "insufficient_data"

    def sources_by_type(
        self,
        sources: list[ApprovedCompanySource],
        source_types: set[CompanyResearchSourceType],
    ) -> list[ApprovedCompanySource]:
        """Return sources matching the requested source types."""
        return [source for source in sources if source.source_type in source_types and source.text]
