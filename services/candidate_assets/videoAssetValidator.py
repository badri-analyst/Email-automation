"""Video asset validation and classification."""

from urllib.parse import urlsplit

from schemas.candidateAssetsSchema import VideoAsset
from services.candidate_assets.url_utils import UrlNormalizer


class VideoAssetValidator:
    """Validate supported YouTube/Vimeo links and classify video assets."""

    _allowed_hosts = {"youtube.com", "www.youtube.com", "youtu.be", "vimeo.com", "www.vimeo.com"}

    def __init__(self) -> None:
        self._normalizer = UrlNormalizer()

    def validate(self, url: object, title: str = "") -> tuple[VideoAsset | None, str]:
        """Return video asset metadata and validation status."""
        normalized = self._normalizer.normalize(url)
        if not normalized:
            return None, "missing"

        parsed = urlsplit(normalized)
        if parsed.netloc.casefold() not in self._allowed_hosts:
            return None, "invalid"

        clean_title = self._clean_title(title)
        return VideoAsset(video_type=self._classify(clean_title, normalized), video_title=clean_title, video_url=normalized), "valid"

    @staticmethod
    def _clean_title(title: str) -> str:
        """Clean provided video title without trusting it as instructions."""
        return " ".join(str(title).replace("<", "").replace(">", "").split())[:120]

    @staticmethod
    def _classify(title: str, url: str) -> str:
        """Classify video type from provided title/url hints."""
        text = f"{title} {url}".casefold()
        if "case" in text:
            return "case study"
        if "walkthrough" in text:
            return "project walkthrough"
        if "demo" in text or "portfolio" in text:
            return "portfolio demo"
        return "intro video"
