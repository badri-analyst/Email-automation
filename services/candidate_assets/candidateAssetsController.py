"""Candidate assets and proof controller."""

from schemas.candidateAssetsSchema import CandidateAssetInput, CandidateAssetsOutput
from services.candidate_assets.candidateAssetsRepository import CandidateAssetsRepository
from services.candidate_assets.linkedinAssetValidator import LinkedInAssetValidator
from services.candidate_assets.positioningSummaryBuilder import PositioningSummaryBuilder
from services.candidate_assets.proofSnippetBuilder import ProofSnippetBuilder
from services.candidate_assets.proofStatusService import ProofStatusService
from services.candidate_assets.resumeAssetManager import ResumeAssetManager
from services.candidate_assets.url_utils import UrlNormalizer
from services.candidate_assets.videoAssetValidator import VideoAssetValidator
from services.candidate_assets.whyRelevantBuilder import WhyRelevantBuilder
from utils.logger import get_logger

logger = get_logger(__name__)


class CandidateAssetsController:
    """Prepare recruiter-safe candidate proof assets."""

    def __init__(self, repository: CandidateAssetsRepository | None = None, max_attempts: int = 2) -> None:
        self._linkedin = LinkedInAssetValidator()
        self._video = VideoAssetValidator()
        self._resume = ResumeAssetManager()
        self._positioning = PositioningSummaryBuilder()
        self._proof = ProofSnippetBuilder()
        self._why = WhyRelevantBuilder()
        self._status = ProofStatusService()
        self._url = UrlNormalizer()
        self._repository = repository or CandidateAssetsRepository()
        self._max_attempts = max(1, max_attempts)

    def process(self, payload: CandidateAssetInput | dict[str, object]) -> CandidateAssetsOutput:
        """Process one candidate asset payload with failure isolation."""
        for attempt in range(1, self._max_attempts + 1):
            try:
                request = payload if isinstance(payload, CandidateAssetInput) else CandidateAssetInput.model_validate(payload)
                return self._process_once(request)
            except Exception as exc:
                logger.exception("Candidate assets attempt %s failed", attempt)
                if attempt == self._max_attempts:
                    return CandidateAssetsOutput(
                        proof_status="proof_processing_failed",
                        proof_reason=str(exc) or "Candidate proof processing failed.",
                        manual_review_flag=True,
                    )
        return CandidateAssetsOutput(proof_status="proof_processing_failed", manual_review_flag=True)

    def _process_once(self, request: CandidateAssetInput) -> CandidateAssetsOutput:
        """Run one deterministic processing pass."""
        cached = self._repository.get(request.campaign_id, request.candidate_id) if request.campaign_id and request.candidate_id else None
        if cached:
            return cached

        linkedin_url, linkedin_status = self._linkedin.validate(request.linkedin_url)
        resume = self._resume.build(request.resume_url, request.resume_metadata)
        video, video_status = self._video.validate(request.youtube_video_url)
        videos = [video] if video else []
        portfolio_assets, invalid_portfolio = self._normalize_portfolio(request.portfolio_links)
        snippets, proof_manual_review = self._proof.build(request.candidate_proof_points)
        positioning = self._positioning.build(
            request.candidate_positioning,
            request.target_role,
            request.role_country_positioning,
        )
        why_relevant = self._why.build(snippets, positioning)
        asset_types = self._asset_types(linkedin_status, resume.resume_available, videos, portfolio_assets)
        invalid_links = linkedin_status == "invalid" or video_status == "invalid" or invalid_portfolio
        status, reason = self._status.assign(
            linkedin_status,
            resume.resume_available,
            len(videos),
            len(portfolio_assets),
            snippets,
            invalid_links,
            proof_manual_review,
        )
        output = CandidateAssetsOutput(
            campaign_id=request.campaign_id,
            candidate_id=request.candidate_id,
            proof_status=status,
            proof_reason=reason,
            linkedin_profile_url=linkedin_url,
            linkedin_profile_status=linkedin_status,
            resume_reference=resume,
            video_assets=videos,
            portfolio_assets=portfolio_assets,
            professional_positioning_summary=positioning,
            why_relevant_summary=why_relevant,
            candidate_proof_snippets=snippets,
            asset_types_detected=asset_types,
            manual_review_flag=proof_manual_review,
        )
        self._repository.save(output)
        return output

    def _normalize_portfolio(self, links: list[str]) -> tuple[list[str], bool]:
        """Normalize portfolio links and detect invalid links."""
        normalized_links: list[str] = []
        invalid = False
        for link in links:
            normalized = self._url.normalize(link)
            if normalized:
                normalized_links.append(normalized)
            elif link:
                invalid = True
        return list(dict.fromkeys(normalized_links)), invalid

    @staticmethod
    def _asset_types(linkedin_status: str, resume_available: bool, videos: list[object], portfolio: list[str]) -> list[str]:
        """Return detected asset types."""
        assets: list[str] = []
        if linkedin_status == "valid":
            assets.append("linkedin_profile")
        if resume_available:
            assets.append("resume")
        for video in videos:
            assets.append("intro_video" if video.video_type == "intro video" else "project_case_study")
        for link in portfolio:
            if "github.com" in link:
                assets.append("github")
            else:
                assets.append("portfolio")
        return list(dict.fromkeys(assets))
