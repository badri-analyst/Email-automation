"""Candidate positioning builder."""


class CandidatePositioningService:
    """Position the candidate using FinalPersonalizationPayload fields."""

    def build(self, payload: dict) -> str:
        candidate = payload.get("candidate", {})
        prospect = payload.get("prospect", {})
        key_skills = payload.get("key_skills") or []

        name = str(candidate.get("full_name") or "").strip()
        current_role = str(candidate.get("current_role") or "").strip()
        why_relevant = str(candidate.get("why_relevant") or "").strip()
        role = str(prospect.get("role") or current_role or "Business Analyst").strip()

        skill_phrase = f", specialising in {key_skills[0]}" if key_skills else ""
        intro = f"I am {name}, a {current_role}{skill_phrase}." if name and current_role else f"I am a {role} professional{skill_phrase}."

        if why_relevant:
            return f"{intro} {why_relevant}"
        return intro
