"""JSON validation helpers for LinkedIn research output."""

from typing import Any

from pydantic import ValidationError

from schemas.research_schema import LinkedInResearchOutput


class ResearchJsonValidator:
    """Validate deterministic LinkedIn research JSON payloads."""

    def validate(self, payload: dict[str, Any]) -> LinkedInResearchOutput:
        """Return a validated research output model or raise ValidationError."""
        return LinkedInResearchOutput.model_validate(payload)

    def is_valid(self, payload: dict[str, Any]) -> bool:
        """Return True when payload conforms to the stable research schema."""
        try:
            self.validate(payload)
        except ValidationError:
            return False
        return True
