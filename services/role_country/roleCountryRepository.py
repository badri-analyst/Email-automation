"""Campaign-level role-country intelligence repository."""

from schemas.roleCountrySchema import RoleCountryOutput


class RoleCountryRepository:
    """In-memory cache for duplicate role-country combinations."""

    def __init__(self) -> None:
        self._store: dict[tuple[str, str, str, str, str], RoleCountryOutput] = {}

    def get(
        self,
        campaign_id: str,
        normalized_role: str,
        normalized_country: str,
        industry: str,
        seniority_level: str,
    ) -> RoleCountryOutput | None:
        """Return cached intelligence."""
        return self._store.get(self._key(campaign_id, normalized_role, normalized_country, industry, seniority_level))

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
        self._store[self._key(campaign_id, normalized_role, normalized_country, industry, seniority_level)] = output

    @staticmethod
    def _key(
        campaign_id: str,
        normalized_role: str,
        normalized_country: str,
        industry: str,
        seniority_level: str,
    ) -> tuple[str, str, str, str, str]:
        """Return deterministic cache key."""
        return (
            campaign_id,
            normalized_role.casefold(),
            normalized_country.casefold(),
            industry.casefold(),
            seniority_level.casefold(),
        )
