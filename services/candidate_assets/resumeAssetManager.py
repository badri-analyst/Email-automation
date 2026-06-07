"""Resume reference normalization."""

from schemas.candidateAssetsSchema import ResumeReference
from services.candidate_assets.url_utils import UrlNormalizer


class ResumeAssetManager:
    """Preserve safe resume metadata only."""

    def __init__(self) -> None:
        self._normalizer = UrlNormalizer()

    def build(self, resume_url: object, metadata: dict) -> ResumeReference:
        """Return safe resume reference."""
        if metadata:
            return ResumeReference(resume_available=True, resume_type="uploaded_metadata", resume_reference_url="")

        normalized = self._normalizer.normalize(resume_url)
        if not normalized:
            return ResumeReference()

        resume_type = "cloud_document" if any(host in normalized for host in ("drive.google.com", "sharepoint.com", "docs.google.com")) else "url"
        return ResumeReference(resume_available=True, resume_type=resume_type, resume_reference_url=normalized)
