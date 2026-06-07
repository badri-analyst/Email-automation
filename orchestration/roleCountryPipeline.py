"""Batch orchestration for role-country intelligence."""

from schemas.roleCountrySchema import RoleCountryInput, RoleCountryOutput
from services.role_country.roleCountryIntelligenceController import RoleCountryIntelligenceController
from services.role_country.roleCountryRepository import RoleCountryRepository


class RoleCountryPipeline:
    """Campaign-level role-country intelligence pipeline with duplicate caching."""

    def __init__(self, repository: RoleCountryRepository | None = None) -> None:
        self._repository = repository or RoleCountryRepository()
        self._controller = RoleCountryIntelligenceController(repository=self._repository)

    def build_intelligence(self, payload: RoleCountryInput | dict[str, object]) -> RoleCountryOutput:
        """Build intelligence for one prospect."""
        return self._controller.build(payload)

    def build_batch(self, payloads: list[RoleCountryInput | dict[str, object]]) -> list[RoleCountryOutput]:
        """Build intelligence for a campaign batch."""
        return [self.build_intelligence(payload) for payload in payloads]
