"""Campaign role-country cache facade."""

from schemas.roleCountrySchema import RoleCountryOutput
from services.role_country.roleCountryRepository import RoleCountryRepository


class RoleCountryCache:
    """Facade over the role-country repository for campaign execution."""

    def __init__(self) -> None:
        self._repository = RoleCountryRepository()

    @property
    def repository(self) -> RoleCountryRepository:
        """Return repository for pipeline injection."""
        return self._repository

    def get(
        self,
        campaign_id: str,
        normalized_role: str,
        normalized_country: str,
        industry: str,
        seniority_level: str,
    ) -> RoleCountryOutput | None:
        """Return cached intelligence."""
        return self._repository.get(campaign_id, normalized_role, normalized_country, industry, seniority_level)

    def save(
        self,
        campaign_id: str,
        normalized_role: str,
        normalized_country: str,
        industry: str,
        seniority_level: str,
        output: RoleCountryOutput,
    ) -> None:
        """Cache intelligence."""
        self._repository.save(campaign_id, normalized_role, normalized_country, industry, seniority_level, output)
