"""LinkedIn profile asset validation."""

from urllib.parse import urlsplit

from services.candidate_assets.url_utils import UrlNormalizer


class LinkedInAssetValidator:
    """Validate and normalize candidate LinkedIn profile URLs."""

    def __init__(self) -> None:
        self._normalizer = UrlNormalizer()

    def validate(self, url: object) -> tuple[str, str]:
        """Return normalized LinkedIn URL and status."""
        normalized = self._normalizer.normalize(url)
        if not normalized:
            return "", "missing"

        parsed = urlsplit(normalized)
        host = parsed.netloc.casefold()
        path = parsed.path.rstrip("/")
        if host not in {"linkedin.com", "www.linkedin.com"}:
            return normalized, "invalid"
        if not (path.startswith("/in/") or path.startswith("/pub/")):
            return normalized, "invalid"
        return normalized.replace("https://www.linkedin.com", "https://linkedin.com"), "valid"
