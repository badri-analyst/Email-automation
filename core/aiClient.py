"""Python AI client supporting NVIDIA NIM and Google Gemini.

Accepts api_key directly (from candidate profile) or falls back to env vars.
Auto-detects provider from key prefix:
  - nvapi-*  → NVIDIA NIM
  - AIza*    → Google Gemini (OpenAI-compatible endpoint)
"""

import json
import os
import urllib.error
import urllib.request
from typing import Any

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
DEFAULT_TIMEOUT = 90  # seconds

MODULE_CONFIG: dict[str, dict[str, str]] = {
    "company-research": {
        "nvidia_model": "meta/llama-4-maverick-17b-128e-instruct",
        "gemini_model": "gemini-1.5-flash",
        "api_key_env": "COMPANY_RESEARCH_API_KEY",
        "backup_key_env": "COMPANY_RESEARCH_BACKUP_KEY",
    },
    "email-personalization": {
        "nvidia_model": "mistralai/mistral-large-3-675b-instruct-2512",
        "gemini_model": "gemini-1.5-flash",
        "api_key_env": "EMAIL_WRITING_API_KEY",
        "backup_key_env": "EMAIL_WRITING_BACKUP_KEY",
    },
}


def detect_provider(api_key: str) -> str:
    """Return 'gemini' or 'nvidia' based on key prefix."""
    if api_key.startswith("AIza"):
        return "gemini"
    return "nvidia"


def _get_base_url(provider: str) -> str:
    if provider == "gemini":
        return GEMINI_BASE_URL
    return os.environ.get("NVIDIA_API_BASE_URL", NVIDIA_BASE_URL).rstrip("/")


def _get_model(module_name: str, provider: str) -> str:
    config = MODULE_CONFIG.get(module_name, {})
    if provider == "gemini":
        return config.get("gemini_model", "gemini-1.5-flash")
    return config.get("nvidia_model", "mistralai/mistral-large-3-675b-instruct-2512")


def _resolve_key(module_name: str, primary: str = "", backup: str = "") -> tuple[str, str]:
    """Return (primary_key, backup_key) — candidate keys take priority over env vars."""
    config = MODULE_CONFIG.get(module_name, {})
    resolved_primary = (
        primary
        or os.environ.get(config.get("api_key_env", ""), "")
        or os.environ.get("NVIDIA_API_KEY", "")
        or os.environ.get("AI_API_KEY", "")
    )
    resolved_backup = (
        backup
        or os.environ.get(config.get("backup_key_env", ""), "")
    )
    return resolved_primary, resolved_backup


def _call_once(api_key: str, module_name: str, system_prompt: str, user_message: str, temperature: float, max_tokens: int) -> dict[str, Any]:
    """Make one API call with a specific key. Raises RuntimeError on failure."""
    if not api_key:
        raise RuntimeError(f"No API key provided for module '{module_name}'.")

    provider = detect_provider(api_key)
    url = f"{_get_base_url(provider)}/chat/completions"
    model = _get_model(module_name, provider)

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
        raise RuntimeError(f"AI API HTTP {exc.code} for '{module_name}' ({provider}): {body}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"AI API connection error for '{module_name}': {exc.reason}") from exc
    except TimeoutError as exc:
        raise RuntimeError(f"AI API timed out after {DEFAULT_TIMEOUT}s for '{module_name}'") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"AI API returned non-JSON for '{module_name}'") from exc

    content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    if not content:
        raise RuntimeError(f"AI API returned empty content for '{module_name}'")

    # Strip markdown code fences if present
    if content.startswith("```"):
        lines = content.splitlines()
        inner = lines[1:] if len(lines) > 1 else lines
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        content = "\n".join(inner).strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"AI response for '{module_name}' was not valid JSON: {content[:200]}") from exc


def call_ai(
    module_name: str,
    system_prompt: str,
    user_message: str,
    temperature: float = 0.3,
    max_tokens: int = 2000,
    api_key: str = "",
    backup_api_key: str = "",
) -> dict[str, Any]:
    """Call AI with primary key, fallback to backup on failure.

    Args:
        module_name: Pipeline step name.
        system_prompt: System-level instruction.
        user_message: User-level payload (serialised JSON).
        temperature: Sampling temperature.
        max_tokens: Max tokens in response.
        api_key: Candidate's primary API key (overrides env var).
        backup_api_key: Candidate's backup API key (used if primary fails).

    Returns:
        Parsed dict from AI response.

    Raises:
        RuntimeError: If both keys fail or no keys are configured.
    """
    primary, backup = _resolve_key(module_name, api_key, backup_api_key)

    # Try primary key
    if primary:
        try:
            return _call_once(primary, module_name, system_prompt, user_message, temperature, max_tokens)
        except RuntimeError as primary_err:
            if backup:
                pass  # fall through to backup
            else:
                raise RuntimeError(f"API key failed: {primary_err}") from primary_err

    # Try backup key
    if backup:
        try:
            return _call_once(backup, module_name, system_prompt, user_message, temperature, max_tokens)
        except RuntimeError as backup_err:
            raise RuntimeError(f"Both API keys failed. Primary: {primary_err if primary else 'not set'}. Backup: {backup_err}") from backup_err

    raise RuntimeError(
        f"No API key configured for '{module_name}'. "
        "Please add your API key in your candidate profile."
    )


def is_ai_configured(module_name: str, api_key: str = "", backup_api_key: str = "") -> bool:
    """Return True if at least one API key is available for this module."""
    primary, backup = _resolve_key(module_name, api_key, backup_api_key)
    return bool(primary or backup)
