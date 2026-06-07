"""Company website inference and validation."""

import re
from urllib.parse import urlsplit, urlunsplit

from schemas.companyResearchSchema import CompanyWebsiteStatus


class CompanyWebsiteService:
    """Validate and infer company website URLs from approved inputs."""

    _domain_pattern = re.compile(r"^[a-z0-9.-]+\.[a-z]{2,}$", re.IGNORECASE)
    _unsafe_hosts = {"linkedin.com", "www.linkedin.com", "gmail.com", "yahoo.com", "hotmail.com", "outlook.com"}

    def validate(self, website: object) -> tuple[str, CompanyWebsiteStatus]:
        """Return normalized website URL and status."""
        if website is None or not str(website).strip():
            return "", "missing"

        text = str(website).strip()
        candidate = text if "://" in text else f"https://{text}"
        parsed = urlsplit(candidate)
        host = parsed.netloc.casefold()
        if not host or host in self._unsafe_hosts or not self._domain_pattern.match(host):
            return text, "invalid"

        path = parsed.path.rstrip("/")
        return urlunsplit(("https", host, path, "", "")), "valid"

    def infer_from_email_domain(self, email: object) -> tuple[str, CompanyWebsiteStatus]:
        """Infer a website from a non-consumer email domain."""
        if email is None or "@" not in str(email):
            return "", "missing"

        domain = str(email).split("@")[-1].strip().casefold()
        if domain in self._unsafe_hosts or not self._domain_pattern.match(domain):
            return "", "missing"
        return f"https://{domain}", "inferred"

    def infer_from_company_name(self, company_name: object) -> tuple[str, CompanyWebsiteStatus]:
        """Infer a possible website from company name when no stronger source exists."""
        if company_name is None or not str(company_name).strip():
            return "", "missing"

        slug = re.sub(r"[^a-z0-9]+", "", str(company_name).casefold())
        if not slug:
            return "", "missing"
        return f"https://{slug}.com", "inferred"
