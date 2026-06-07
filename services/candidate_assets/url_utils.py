"""Safe URL normalization utilities for candidate assets."""

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


class UrlNormalizer:
    """Normalize URLs while preserving valid identifiers and removing tracking."""

    _tracking_prefixes = ("utm_",)
    _tracking_params = {"trk", "fbclid", "gclid", "mc_cid", "mc_eid"}

    def normalize(self, url: object) -> str:
        """Return normalized URL or empty string."""
        if url is None or not str(url).strip():
            return ""

        text = str(url).strip()
        candidate = text if "://" in text else f"https://{text}"
        parsed = urlsplit(candidate)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            return ""

        host = parsed.netloc.casefold()
        path = "/".join(segment for segment in parsed.path.split("/") if segment)
        query = urlencode(
            [
                (key, value)
                for key, value in parse_qsl(parsed.query, keep_blank_values=False)
                if key.casefold() not in self._tracking_params
                and not key.casefold().startswith(self._tracking_prefixes)
            ]
        )
        return urlunsplit(("https", host, f"/{path}" if path else "", query, ""))
