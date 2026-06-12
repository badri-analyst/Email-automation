"""AI-powered email generation using NVIDIA Mistral Large."""

import json
from pathlib import Path

from core.aiClient import call_ai, is_ai_configured
from utils.logger import get_logger

logger = get_logger(__name__)

_PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "email_generation_prompt.txt"
_MODULE = "email-personalization"


def _load_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8").strip()


def enhance(input_data: dict) -> dict | None:
    """Call AI to generate a personalised outreach email.

    Returns a dict with subject_line, email_body, tone_used, and
    email_generation_status on success.
    Returns None if AI is not configured or the call fails.
    """
    if not is_ai_configured(_MODULE):
        logger.debug("Email generation AI not configured — using deterministic builder.")
        return None

    payload = input_data.get("final_personalization_payload", {})

    user_message = json.dumps({
        "opening_hook": payload.get("opening_hook", ""),
        "candidate": payload.get("candidate", {}),
        "prospect": payload.get("prospect", {}),
        "key_skills": payload.get("key_skills", []),
        "tone_guidance": payload.get("tone_guidance", ""),
    }, ensure_ascii=False)

    try:
        result = call_ai(
            module_name=_MODULE,
            system_prompt=_load_prompt(),
            user_message=user_message,
            temperature=0.4,
            max_tokens=1200,
        )
        logger.info("Email generation AI call succeeded for prospect_id='%s'",
                    input_data.get("prospect_id", "unknown"))
        return result
    except Exception as exc:
        logger.warning("Email generation AI call failed — falling back to deterministic builder: %s", exc)
        return None
