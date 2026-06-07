"""AI-powered role-country intelligence using NVIDIA Nemotron 4B."""

import json
from pathlib import Path

from core.aiClient import call_ai, is_ai_configured
from utils.logger import get_logger

logger = get_logger(__name__)

_PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "role_country_prompt.txt"
_MODULE = "role-country"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8").strip()


def enhance(input_data: dict) -> dict | None:
    """Call AI to produce role-country intelligence.

    Returns a dict with AI-generated fields on success.
    Returns None if AI is not configured or the call fails,
    so the caller can fall back to the deterministic pipeline.
    """
    if not is_ai_configured(_MODULE):
        logger.debug("Role-country AI not configured — using deterministic pipeline.")
        return None

    user_message = json.dumps({
        "target_role": input_data.get("target_role", ""),
        "target_country": input_data.get("target_country", ""),
        "industry": input_data.get("industry", ""),
        "seniority_level": input_data.get("seniority_level", ""),
        "candidate_positioning": input_data.get("candidate_positioning", ""),
    }, ensure_ascii=False)

    try:
        result = call_ai(
            module_name=_MODULE,
            system_prompt=_load_prompt(),
            user_message=user_message,
            temperature=0.2,
            max_tokens=1500,
        )
        logger.info("Role-country AI call succeeded for role='%s' country='%s'",
                    input_data.get("target_role"), input_data.get("target_country"))
        return result
    except Exception as exc:
        logger.warning("Role-country AI call failed — falling back to deterministic: %s", exc)
        return None
