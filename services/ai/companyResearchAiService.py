"""AI-powered company research using NVIDIA Llama 4 Maverick."""

import json
from pathlib import Path

from core.aiClient import call_ai, is_ai_configured
from utils.logger import get_logger

logger = get_logger(__name__)

_PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "company_research_prompt.txt"
_MODULE = "company-research"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8").strip()


def enhance(input_data: dict) -> dict | None:
    """Call AI to produce company research output.

    Returns a dict with AI-generated fields on success.
    Returns None if AI is not configured or the call fails,
    so the caller can fall back to the deterministic pipeline.
    """
    if not is_ai_configured(_MODULE):
        logger.debug("Company research AI not configured — using deterministic pipeline.")
        return None

    user_message = json.dumps({
        "company_name": input_data.get("company_name", ""),
        "company_website": input_data.get("company_website", ""),
        "company_linkedin_url": input_data.get("company_linkedin_url", ""),
        "target_role": input_data.get("target_role", ""),
        "target_country": input_data.get("target_country", ""),
        "approved_sources": input_data.get("approved_sources", []),
        "prospect_email": input_data.get("prospect_email", ""),
    }, ensure_ascii=False)

    try:
        result = call_ai(
            module_name=_MODULE,
            system_prompt=_load_prompt(),
            user_message=user_message,
            temperature=0.3,
            max_tokens=1500,
        )
        logger.info("Company research AI call succeeded for '%s'", input_data.get("company_name"))
        return result
    except Exception as exc:
        logger.warning("Company research AI call failed — falling back to deterministic: %s", exc)
        return None
