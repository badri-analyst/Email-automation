"""AI-powered LinkedIn research using NVIDIA Mistral Large."""

import json
from pathlib import Path

from core.aiClient import call_ai, is_ai_configured
from utils.logger import get_logger

logger = get_logger(__name__)

_PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "linkedin_research_prompt.txt"
_MODULE = "linkedin-research"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8").strip()


def enhance(input_data: dict) -> dict | None:
    """Call AI to produce LinkedIn research output.

    Returns a dict with AI-generated fields on success.
    Returns None if AI is not configured or the call fails,
    so the caller can fall back to the deterministic pipeline.
    """
    if not is_ai_configured(_MODULE):
        logger.debug("LinkedIn research AI not configured — using deterministic pipeline.")
        return None

    user_message = json.dumps({
        "full_name": input_data.get("full_name", ""),
        "role_title": input_data.get("role_title", ""),
        "company_name": input_data.get("company_name", ""),
        "linkedin_url": input_data.get("linkedin_url", ""),
        "country": input_data.get("country", ""),
        "industry": input_data.get("industry", ""),
        "profile_summary": input_data.get("profile_summary", ""),
        "bio": input_data.get("bio", ""),
        "posts": input_data.get("posts", []),
        "company_content": input_data.get("company_content", ""),
        "interviews": input_data.get("interviews", []),
        "company_updates": input_data.get("company_updates", []),
    }, ensure_ascii=False)

    try:
        result = call_ai(
            module_name=_MODULE,
            system_prompt=_load_prompt(),
            user_message=user_message,
            temperature=0.3,
            max_tokens=2000,
        )
        logger.info("LinkedIn research AI call succeeded for '%s' at '%s'",
                    input_data.get("full_name"), input_data.get("company_name"))
        return result
    except Exception as exc:
        logger.warning("LinkedIn research AI call failed — falling back to deterministic: %s", exc)
        return None
