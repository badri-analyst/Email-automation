"""Candidate proof-point selection."""


class CandidateProofPointService:
    """Use key_skills and candidate data from FinalPersonalizationPayload."""

    def build(self, payload: dict) -> str:
        key_skills = payload.get("key_skills") or []
        candidate = payload.get("prospect", {})
        company = str(candidate.get("company") or "your team").strip()

        if len(key_skills) >= 2:
            return f"My focus has been on {key_skills[0]} and {key_skills[1]} — areas I think would be relevant to {company}."
        if key_skills:
            return f"My focus has been on {key_skills[0]} — something I think would add value to {company}."
        return "I can share a concise example of how I approach stakeholder alignment and workflow clarity."
