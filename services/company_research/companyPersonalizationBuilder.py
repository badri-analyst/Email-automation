"""Company-level personalization hook generation."""

from schemas.companyResearchSchema import CompanyRecentUpdate
from schemas.companyResearchSchema import INSUFFICIENT_DATA


class CompanyPersonalizationBuilder:
    """Build safe company-level outreach hooks and professional angle."""

    def role_relevance(self, target_role: str, overview: str, products_services: str) -> str:
        """Return role relevance context when enough context exists."""
        if not target_role or (overview == INSUFFICIENT_DATA and products_services == INSUFFICIENT_DATA):
            return INSUFFICIENT_DATA
        return f"{target_role} experience can be positioned around improving clarity, execution, and measurable business workflows."

    def country_relevance(self, target_country: str, growth_signal: str) -> str:
        """Return country relevance context when applicable."""
        if not target_country:
            return INSUFFICIENT_DATA
        if growth_signal == INSUFFICIENT_DATA:
            return f"Use {target_country} context only if the outreach is locally relevant and supported by the sender's background."
        return f"Mention {target_country} relevance only in connection with the observed growth or hiring context."

    def hooks(
        self,
        updates: list[CompanyRecentUpdate],
        values_summary: str,
        growth_signal: str,
        role_relevance: str,
    ) -> list[str]:
        """Return one to three concise, evidence-bound company personalization hooks."""
        hooks: list[str] = []
        if updates:
            hooks.append(f"Reference the company update: {updates[0].update} Evidence: {updates[0].evidence}")
        if values_summary != INSUFFICIENT_DATA:
            hooks.append(f"Connect to company values/culture: {values_summary} Evidence: {values_summary}")
        if growth_signal != INSUFFICIENT_DATA:
            hooks.append(f"Use growth or hiring context: {growth_signal} Evidence: {growth_signal}")
        if role_relevance != INSUFFICIENT_DATA and not hooks:
            hooks.append(f"Frame the message around role relevance: {role_relevance} Evidence: cleaned role/company context.")
        return hooks[:3] if hooks else [INSUFFICIENT_DATA]

    def email_angle(self, hooks: list[str], role_relevance: str) -> str:
        """Return a safe professional outreach angle without manipulation."""
        if hooks == [INSUFFICIENT_DATA] and role_relevance == INSUFFICIENT_DATA:
            return INSUFFICIENT_DATA
        return "Use a concise, factual note that connects the candidate's relevant experience to observable company context."
