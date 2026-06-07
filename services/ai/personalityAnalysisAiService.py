"""AI-powered communication signal analysis using NVIDIA Step Flash."""

import json
from pathlib import Path

from core.aiClient import call_ai, is_ai_configured
from utils.logger import get_logger

logger = get_logger(__name__)

_PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "personality_analysis_prompt.txt"
_MODULE = "personality-analysis"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8").strip()


def enhance(input_data: dict) -> dict | None:
    """Call AI to produce communication signal output.

    Returns a dict with AI-generated fields on success.
    Returns None if AI is not configured or the call fails,
    so the caller can fall back to the deterministic pipeline.
    """
    if not is_ai_configured(_MODULE):
        logger.debug("Personality analysis AI not configured — using deterministic pipeline.")
        return None

    user_message = json.dumps({
        "person_name": input_data.get("person_name", ""),
        "job_title": input_data.get("job_title", ""),
        "company_name": input_data.get("company_name", ""),
        "linkedin_profile_summary": input_data.get("linkedin_profile_summary", ""),
        "linkedin_posts_summary": input_data.get("linkedin_posts_summary", ""),
        "company_research_summary": input_data.get("company_research_summary", ""),
        "role_country_intelligence": input_data.get("role_country_intelligence", ""),
    }, ensure_ascii=False)

    try:
        result = call_ai(
            module_name=_MODULE,
            system_prompt=_load_prompt(),
            user_message=user_message,
            temperature=0.3,
            max_tokens=1500,
        )
        logger.info("Personality analysis AI call succeeded for '%s' at '%s'",
                    input_data.get("person_name"), input_data.get("company_name"))
        return result
    except Exception as exc:
        logger.warning("Personality analysis AI call failed — falling back to deterministic: %s", exc)
        return None
