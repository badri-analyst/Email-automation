"""Shared constants used across the application."""

REQUIRED_COLUMNS: tuple[str, ...] = ("Name", "Email", "Company", "Role", "Country")

NORMALIZED_REQUIRED_COLUMNS: dict[str, str] = {
    "name": "Name",
    "email": "Email",
    "company": "Company",
    "role": "Role",
    "country": "Country",
}

COUNTRY_NORMALIZATION_MAP: dict[str, str] = {
    "usa": "United States",
    "u.s.a": "United States",
    "u.s.a.": "United States",
    "us": "United States",
    "u.s.": "United States",
    "united states of america": "United States",
    "america": "United States",
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
    "great britain": "United Kingdom",
    "britain": "United Kingdom",
    "england": "United Kingdom",
    "uae": "United Arab Emirates",
    "u.a.e.": "United Arab Emirates",
    "emirates": "United Arab Emirates",
}

OUTREACH_COLUMN_ALIAS_MAP: dict[str, str] = {
    "name": "name",
    "full name": "name",
    "fullname": "name",
    "contact name": "name",
    "email": "email",
    "email address": "email",
    "work email": "email",
    "company": "company",
    "company name": "company",
    "company_name": "company",
    "organization": "company",
    "organisation": "company",
    "org": "company",
    "role": "role",
    "title": "role",
    "job title": "role",
    "role title": "role",
    "linkedin": "linkedin_url",
    "linkedin url": "linkedin_url",
    "linkedin_url": "linkedin_url",
    "linkedin profile": "linkedin_url",
    "profile url": "linkedin_url",
    "country": "country",
    "location country": "country",
    "validation status": "validation_status",
    "validation_status": "validation_status",
    "status": "validation_status",
}

COMPANY_LEGAL_SUFFIXES: tuple[str, ...] = (
    "LLC",
    "Inc",
    "Ltd",
    "Pvt Ltd",
    "Corporation",
    "GmbH",
    "LLP",
)

SENIORITY_KEYWORD_MAP: dict[str, tuple[str, ...]] = {
    "executive": (
        "chief",
        "ceo",
        "cfo",
        "coo",
        "cto",
        "cio",
        "cmo",
        "founder",
        "co-founder",
        "president",
        "vice president",
        "vp",
        "head",
        "director",
    ),
    "senior": ("senior", "sr", "principal", "lead", "staff"),
    "manager": ("manager", "mgr", "supervisor"),
    "individual_contributor": (
        "engineer",
        "developer",
        "analyst",
        "specialist",
        "associate",
        "consultant",
    ),
    "entry": ("intern", "trainee", "junior", "jr"),
}

DEPARTMENT_KEYWORD_MAP: dict[str, tuple[str, ...]] = {
    "engineering": (
        "engineering",
        "engineer",
        "developer",
        "software",
        "platform",
        "infrastructure",
        "devops",
        "data",
        "ai",
        "ml",
    ),
    "marketing": ("marketing", "growth", "brand", "content", "demand generation"),
    "sales": ("sales", "account executive", "business development", "revenue"),
    "finance": ("finance", "financial", "accounting", "controller", "cfo"),
    "operations": ("operations", "ops", "chief operating", "supply chain"),
    "human_resources": ("human resources", "people", "talent", "recruiting", "hr"),
    "product": ("product", "program manager", "product manager"),
    "customer_success": ("customer success", "support", "customer experience"),
    "legal": ("legal", "counsel", "compliance"),
}

VALID_CLEANING_INPUT_STATUSES: tuple[str, ...] = ("valid", "validated", "clean", "ready")
