"""Role-country intelligence controller."""

from schemas.roleCountrySchema import INSUFFICIENT_DATA, RoleCountryInput, RoleCountryOutput
from services.role_country.countryNormalizationService import CountryNormalizationService
from services.role_country.countryRoleExpectationService import CountryRoleExpectationService
from services.role_country.emailPositioningService import EmailPositioningService
from services.role_country.proofPointService import ProofPointService
from services.role_country.roleCountryRepository import RoleCountryRepository
from services.role_country.roleCountryStatusService import RoleCountryStatusService
from services.role_country.roleKnowledgeService import RoleKnowledgeService
from services.role_country.roleNormalizationService import RoleNormalizationService
from services.role_country.skillKeywordService import SkillKeywordService
from utils.logger import get_logger

logger = get_logger(__name__)


class RoleCountryIntelligenceController:
    """Generate deterministic role-country intelligence from configured rules."""

    def __init__(self, repository: RoleCountryRepository | None = None, max_attempts: int = 2) -> None:
        self._role_normalizer = RoleNormalizationService()
        self._country_normalizer = CountryNormalizationService()
        self._role_knowledge = RoleKnowledgeService()
        self._country_expectations = CountryRoleExpectationService()
        self._skill_keywords = SkillKeywordService()
        self._positioning = EmailPositioningService()
        self._proof_points = ProofPointService()
        self._status = RoleCountryStatusService()
        self._repository = repository or RoleCountryRepository()
        self._max_attempts = max(1, max_attempts)

    def build(self, payload: RoleCountryInput | dict[str, object]) -> RoleCountryOutput:
        """Build role-country intelligence with per-row failure isolation."""
        for attempt in range(1, self._max_attempts + 1):
            try:
                request = payload if isinstance(payload, RoleCountryInput) else RoleCountryInput.model_validate(payload)
                return self._build_once(request)
            except Exception as exc:
                logger.exception("Role-country intelligence attempt %s failed", attempt)
                if attempt == self._max_attempts:
                    return RoleCountryOutput(
                        role_country_status="role_country_research_failed",
                        role_country_reason=str(exc) or "Role-country intelligence failed.",
                    )
        return RoleCountryOutput(role_country_status="role_country_research_failed")

    def _build_once(self, request: RoleCountryInput) -> RoleCountryOutput:
        """Build one deterministic role-country intelligence output."""
        normalized_role = self._role_normalizer.normalize(request.target_role)
        normalized_country = self._country_normalizer.normalize(request.target_country)
        cached = self._repository.get(
            request.campaign_id,
            normalized_role,
            normalized_country,
            request.industry,
            request.seniority_level,
        ) if request.campaign_id else None
        if cached:
            return cached

        role_supported = self._role_knowledge.is_supported(normalized_role)
        country_supported = self._country_expectations.is_supported(normalized_country)
        industry_refinements = self._role_knowledge.industry_refinement(request.industry)
        seniority_refinements = self._role_knowledge.seniority_refinement(request.seniority_level)
        status, reason = self._status.assign(
            has_role=bool(normalized_role),
            role_supported=role_supported,
            has_country=bool(normalized_country),
            country_supported=country_supported,
            industry_used=bool(industry_refinements),
            seniority_used=bool(seniority_refinements),
        )

        if not role_supported:
            output = self._unsupported_output(request, normalized_role, normalized_country, status, reason)
            self._cache(request, normalized_role, normalized_country, output)
            return output

        expectations = (
            self._country_expectations.expectations(normalized_country)
            if country_supported
            else [INSUFFICIENT_DATA]
        )
        country_tone = (
            self._country_expectations.email_tone(normalized_country)
            if country_supported
            else "professional, concise, and evidence-based"
        )
        priority_skills = self._skill_keywords.merge_unique(
            self._role_knowledge.priority_skills(normalized_role),
            industry_refinements,
            seniority_refinements,
        )
        business_keywords = self._skill_keywords.merge_unique(
            self._role_knowledge.business_keywords(normalized_role),
            industry_refinements,
            seniority_refinements,
        )
        proof_points = self._proof_points.build(
            self._role_knowledge.proof_points(normalized_role),
            industry_refinements + seniority_refinements,
        )
        guidance = self._positioning.guidance(
            role=normalized_role,
            country=normalized_country,
            angle=self._role_knowledge.positioning_angle(normalized_role),
            expectations=expectations,
            proof_points=proof_points,
            candidate_positioning=request.candidate_positioning,
        )
        source_type = "configured_role_country_rule" if country_supported else "configured_role_rule"
        if industry_refinements:
            source_type = "configured_industry_refinement"
        elif seniority_refinements:
            source_type = "configured_seniority_refinement"

        output = RoleCountryOutput(
            campaign_id=request.campaign_id,
            prospect_id=request.prospect_id,
            target_role=request.target_role,
            target_country=request.target_country,
            normalized_role=normalized_role,
            normalized_country=normalized_country,
            role_country_status=status,
            role_country_reason=reason,
            intelligence_source_type=source_type,
            role_summary=self._role_knowledge.role_summary(normalized_role),
            core_responsibilities=self._role_knowledge.core_responsibilities(normalized_role),
            country_role_expectations=expectations,
            priority_skills=priority_skills,
            tools_or_frameworks=self._role_knowledge.tools_or_frameworks(normalized_role),
            business_keywords=business_keywords,
            email_positioning_angle=self._role_knowledge.positioning_angle(normalized_role),
            country_specific_email_tone=country_tone,
            proof_points_to_use=proof_points,
            things_to_avoid=self._role_knowledge.things_to_avoid(),
            personalization_guidance=guidance,
        )
        self._cache(request, normalized_role, normalized_country, output)
        return output

    @staticmethod
    def _unsupported_output(
        request: RoleCountryInput,
        normalized_role: str,
        normalized_country: str,
        status: str,
        reason: str,
    ) -> RoleCountryOutput:
        """Return stable insufficient/unsupported output."""
        return RoleCountryOutput(
            campaign_id=request.campaign_id,
            prospect_id=request.prospect_id,
            target_role=request.target_role,
            target_country=request.target_country,
            normalized_role=normalized_role,
            normalized_country=normalized_country,
            role_country_status=status,
            role_country_reason=reason,
        )

    def _cache(
        self,
        request: RoleCountryInput,
        normalized_role: str,
        normalized_country: str,
        output: RoleCountryOutput,
    ) -> None:
        """Cache output for duplicate campaign combinations."""
        if request.campaign_id and normalized_role:
            self._repository.save(
                request.campaign_id,
                normalized_role,
                normalized_country,
                request.industry,
                request.seniority_level,
                output,
            )
