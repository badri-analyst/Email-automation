"""Fallback email builder."""


class FallbackEmailBuilder:
    """Build role-based fallback email using FinalPersonalizationPayload fields."""

    def build(self, payload: dict, cta_sentence: str) -> str:
        prospect = payload.get("prospect", {})
        candidate = payload.get("candidate", {})
        key_skills = payload.get("key_skills") or []

        role = str(prospect.get("role") or "Business Analyst").strip()
        company = str(prospect.get("company") or "your team").strip()
        name = str(candidate.get("full_name") or "").strip()
        current_role = str(candidate.get("current_role") or role).strip()
        skill_phrase = f", with a focus on {key_skills[0]}" if key_skills else ""

        intro = f"I am {name}, a {current_role}{skill_phrase}." if name else f"I am a {current_role}{skill_phrase}."

        phone = str(candidate.get("phone") or "").strip()
        sign_off_lines = ["Regards,", name or ""] + ([phone] if phone else [])
        sign_off = "\n".join(line for line in sign_off_lines if line)

        return "\n\n".join([
            f"I wanted to reach out about {role} opportunities at {company}.",
            intro,
            "I can share a concise example of how I approach requirements clarity, stakeholder alignment, and business-tech communication.",
            cta_sentence,
            sign_off,
        ])
