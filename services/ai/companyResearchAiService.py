"""AI-powered company research using NVIDIA or Gemini."""

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

    Returns a dict on success, None if AI is not configured or call fails.
    """
    api_key = input_data.get("api_key", "") or ""
    backup_api_key = input_data.get("backup_api_key", "") or ""
    base_url = input_data.get("base_url", "") or ""
    model = input_data.get("model", "") or ""

    if not is_ai_configured(_MODULE, api_key, backup_api_key):
        logger.debug("Company research AI not configured — using deterministic pipeline.")
        return None

    user_message = json.dumps({
        "company_name": input_data.get("company_name", ""),
        "company_website": input_data.get("company_website", ""),
        "target_role": input_data.get("target_role", ""),
        "target_country": input_data.get("target_country", ""),
    }, ensure_ascii=False)

    try:
        result = call_ai(
            module_name=_MODULE,
            system_prompt=_load_prompt(),
            user_message=user_message,
            temperature=0.3,
            max_tokens=1500,
            api_key=api_key,
            backup_api_key=backup_api_key,
            base_url=base_url,
            model=model,
        )
        logger.info("Company research AI call succeeded for '%s'", input_data.get("company_name"))
        return result
    except Exception as exc:
        logger.error("Company research AI call FAILED (api_key_prefix=%s, base_url=%s, model=%s): %s",
                     api_key[:10] if api_key else "none", base_url, model, exc)
        return None
