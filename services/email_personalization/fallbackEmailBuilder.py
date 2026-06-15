"""Fallback email builder."""


class FallbackEmailBuilder:
    """Build role-based fallback email using FinalPersonalizationPayload fields."""

    def build(self, payload: dict, cta_sentence: str) -> str:
        prospect = payload.get("prospect", {})
        candidate = payload.get("candidate", {})
        key_skills = payload.get("key_skills") or []

        role = str(prospect.get("role") or "").strip()
        company = str(prospect.get("company") or "your team").strip()
        name = str(candidate.get("full_name") or "").strip()
        display_role = str(candidate.get("current_role") or candidate.get("target_role") or role).strip()
        skill_phrase = f", with a focus on {key_skills[0]}" if key_skills else ""

        if name and display_role:
            intro = f"I am {name}, a {display_role}{skill_phrase}."
        elif name:
            intro = f"I am {name}, reaching out about this opportunity."
        elif display_role:
            intro = f"I am a {display_role} professional{skill_phrase}."
        else:
            intro = "I wanted to introduce myself and explore potential opportunities."

        phone = str(candidate.get("phone") or "").strip()
        sign_off_lines = ["Regards,", name or ""] + ([phone] if phone else [])
        sign_off = "\n".join(line for line in sign_off_lines if line)

        linkedin = str(candidate.get("linkedin_url") or "").strip()
        youtube = str(candidate.get("youtube_url") or "").strip()
        portfolio = str(candidate.get("portfolio_url") or "").strip()
        resume_url = str(candidate.get("resume_url") or "").strip()
        link_lines = []
        if linkedin:
            link_lines.append(f"LinkedIn: {linkedin}")
        if resume_url:
            link_lines.append(f"Resume: {resume_url}")
        if youtube:
            link_lines.append(f"Why Should You Hire Me: {youtube}")
        if portfolio:
            link_lines.append(f"Portfolio: {portfolio}")
        links_block = "\n".join(link_lines)

        opening = f"I wanted to reach out about {display_role} opportunities at {company}." if display_role else f"I wanted to reach out about opportunities at {company}."
        parts = [
            opening,
            intro,
            "I can share a concise example of how I approach requirements clarity, stakeholder alignment, and business-tech communication.",
            cta_sentence,
        ]
        if links_block:
            parts.append(links_block)
        parts.append(sign_off)
        return "\n\n".join(parts)
