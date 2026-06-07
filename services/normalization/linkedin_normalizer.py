"""LinkedIn URL normalization."""

from urllib.parse import urlsplit, urlunsplit


class LinkedInNormalizer:
    """Normalize LinkedIn profile URLs without validating ownership or reachability."""

    _linkedin_hosts = {"linkedin.com", "www.linkedin.com"}

    def normalize(self, value: object) -> str:
        """Return a canonical LinkedIn URL with protocol and no tracking parameters."""
        if value is None:
            return ""

        text = str(value).strip()
        if not text:
            return ""

        candidate = text if "://" in text else f"https://{text}"
        parsed = urlsplit(candidate)
        host = parsed.netloc.casefold()
        path = parsed.path.rstrip("/")

        if host in self._linkedin_hosts:
            host = "linkedin.com"

        if not host:
            return text

        return urlunsplit(("https", host, path, "", ""))
