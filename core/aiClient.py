"""Python AI client for NVIDIA NIM and compatible OpenAI-format APIs.

Used by every AI pipeline step. Falls back gracefully so the deterministic
pipeline can still run when no API key is configured.
"""

import json
import os
import urllib.error
import urllib.request
from typing import Any

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_TIMEOUT = 60  # seconds

# Per-module model + API key configuration.
# Each step can use a different model and a different API key env var.
MODULE_CONFIG: dict[str, dict[str, str]] = {
    "role-country": {
        "model": "nvidia/nemotron-mini-4b-instruct",
        "api_key_env": "ROLE_COUNTRY_API_KEY",
    },
    "linkedin-research": {
        "model": "mistralai/mistral-large-3-675b-instruct-2512",
        "api_key_env": "LINKEDIN_RESEARCH_API_KEY",
    },
    "company-research": {
        "model": "meta/llama-4-maverick-17b-128e-instruct",
        "api_key_env": "COMPANY_RESEARCH_API_KEY",
    },
    "personality-analysis": {
        "model": "stepfun-ai/step-3.5-flash",
        "api_key_env": "COMMUNICATION_SIGNAL_API_KEY",
    },
    "email-personalization": {
        "model": "mistralai/mistral-large-3-675b-instruct-2512",
        "api_key_env": "EMAIL_WRITING_API_KEY",
    },
}


def _get_api_key(module_name: str) -> str:
    """Return the API key for this module, falling back to shared keys."""
    config = MODULE_CONFIG.get(module_name, {})
    return (
        os.environ.get(config.get("api_key_env", ""), "")
        or os.environ.get("NVIDIA_API_KEY", "")
        or os.environ.get("AI_API_KEY", "")
        or os.environ.get("AIMLAPI_API_KEY", "")
        or os.environ.get("OPENAI_API_KEY", "")
    )


def _get_base_url() -> str:
    """Return the API base URL from env or default to NVIDIA NIM."""
    return (
        os.environ.get("NVIDIA_API_BASE_URL", "")
        or os.environ.get("AI_API_BASE_URL", "")
        or NVIDIA_BASE_URL
    ).rstrip("/")


def _get_model(module_name: str) -> str:
    """Return the model name for this module.
    Per-module model takes priority. AI_MODEL is only used when no
    module-specific model is defined (e.g. for unknown/custom modules).
    """
    config = MODULE_CONFIG.get(module_name, {})
    return (
        config.get("model", "")
        or os.environ.get("AI_MODEL", "")
        or "gpt-4o"
    )


def _strip_code_fences(text: str) -> str:
    """Remove markdown code fences that some models wrap around JSON."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        # Drop first line (```json or ```) and last line (```)
        inner = lines[1:] if len(lines) > 1 else lines
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        text = "\n".join(inner).strip()
    return text


def call_ai(
    module_name: str,
    system_prompt: str,
    user_message: str,
    temperature: float = 0.3,
    max_tokens: int = 2000,
) -> dict[str, Any]:
    """Call the AI API and return the parsed JSON response.

    Args:
        module_name: Pipeline step name used to select model and API key.
        system_prompt: The system-level instruction for the model.
        user_message: The user-level payload (typically serialised JSON).
        temperature: Sampling temperature (lower = more deterministic).
        max_tokens: Maximum tokens in the response.

    Returns:
        Parsed dict from the AI response content.

    Raises:
        RuntimeError: Missing API key, HTTP error, or non-JSON response.
    """
    api_key = _get_api_key(module_name)
    if not api_key:
        raise RuntimeError(
            f"No API key configured for module '{module_name}'. "
            "Set NVIDIA_API_KEY or AI_API_KEY in your environment."
        )

    url = f"{_get_base_url()}/chat/completions"
    model = _get_model(module_name)

    payload = json.dumps({
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"AI API HTTP {exc.code} for '{module_name}': {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"AI API connection error for '{module_name}': {exc.reason}") from exc
    except TimeoutError as exc:
        raise RuntimeError(f"AI API timed out after {DEFAULT_TIMEOUT}s for '{module_name}'") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"AI API returned non-JSON response for '{module_name}'") from exc

    content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    if not content:
        raise RuntimeError(f"AI API returned empty content for '{module_name}'")

    content = _strip_code_fences(content)

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"AI response for '{module_name}' was not valid JSON: {content[:200]}"
        ) from exc


def is_ai_configured(module_name: str) -> bool:
    """Return True if an API key is available for this module."""
    return bool(_get_api_key(module_name))
