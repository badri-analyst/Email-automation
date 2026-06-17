"""Universal AI client — works with any OpenAI-compatible API or Google Gemini native API.

Supports:
  - NVIDIA NIM (nvapi-...)
  - Google Gemini native API (AQ.* keys) — uses generateContent endpoint
  - OpenAI, Groq, Together AI, Mistral (standard Bearer token)
"""

import json
import os
import urllib.error
import urllib.request
from typing import Any

DEFAULT_TIMEOUT = 90  # seconds

GEMINI_NATIVE_BASE = "https://generativelanguage.googleapis.com/v1beta/models"

MODULE_CONFIG: dict[str, dict[str, str]] = {
    "company-research": {
        "api_key_env": "COMPANY_RESEARCH_API_KEY",
        "backup_key_env": "COMPANY_RESEARCH_BACKUP_KEY",
        "base_url_env": "COMPANY_RESEARCH_BASE_URL",
        "model_env": "COMPANY_RESEARCH_MODEL",
        "default_base_url": "https://integrate.api.nvidia.com/v1",
        "default_model": "meta/llama-4-maverick-17b-128e-instruct",
        "default_gemini_model": "gemini-2.5-flash-preview-05-20",
    },
    "email-personalization": {
        "api_key_env": "EMAIL_WRITING_API_KEY",
        "backup_key_env": "EMAIL_WRITING_BACKUP_KEY",
        "base_url_env": "EMAIL_WRITING_BASE_URL",
        "model_env": "EMAIL_WRITING_MODEL",
        "default_base_url": "https://integrate.api.nvidia.com/v1",
        "default_model": "mistralai/mistral-large-3-675b-instruct-2512",
        "default_gemini_model": "gemini-2.5-flash-preview-05-20",
    },
}


def _is_gemini_native_key(api_key: str) -> bool:
    """AQ. keys use Gemini native API, not OpenAI-compatible endpoint."""
    return api_key.startswith("AQ.")


def _resolve_config(
    module_name: str,
    api_key: str = "",
    backup_api_key: str = "",
    base_url: str = "",
    model: str = "",
) -> dict[str, Any]:
    config = MODULE_CONFIG.get(module_name, {})
    resolved_key = (
        api_key.strip()
        or os.environ.get(config.get("api_key_env", ""), "")
        or os.environ.get("NVIDIA_API_KEY", "")
        or os.environ.get("AI_API_KEY", "")
        or os.environ.get("OPENAI_API_KEY", "")
    )
    resolved_backup = (
        backup_api_key.strip()
        or os.environ.get(config.get("backup_key_env", ""), "")
    )
    # For Gemini native keys (AQ.), skip NVIDIA defaults entirely
    if _is_gemini_native_key(resolved_key) or _is_gemini_native_key(resolved_backup):
        resolved_base_url = ""
        resolved_model = model.strip() or os.environ.get(config.get("model_env", ""), "") or ""
    else:
        resolved_base_url = (
            base_url.strip()
            or os.environ.get(config.get("base_url_env", ""), "")
            or os.environ.get("AI_API_BASE_URL", "")
            or config.get("default_base_url", "https://integrate.api.nvidia.com/v1")
        ).rstrip("/")
        resolved_model = (
            model.strip()
            or os.environ.get(config.get("model_env", ""), "")
            or os.environ.get("AI_MODEL", "")
            or config.get("default_model", "")
        )
    return {
        "api_key": resolved_key,
        "backup_api_key": resolved_backup,
        "base_url": resolved_base_url,
        "model": resolved_model,
    }


def _strip_code_fences(content: str) -> str:
    if content.startswith("```"):
        lines = content.splitlines()
        inner = lines[1:] if len(lines) > 1 else lines
        if inner and inner[-1].strip() == "```":
            inner = inner[:-1]
        content = "\n".join(inner).strip()
    return content


def _call_gemini_native(
    api_key: str,
    model: str,
    module_name: str,
    system_prompt: str,
    user_message: str,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    """Call Gemini native generateContent API for AQ. keys."""
    # Use default gemini model if none specified or if it looks like an NVIDIA model
    config = MODULE_CONFIG.get(module_name, {})
    gemini_model = model if model and not "/" in model else config.get("default_gemini_model", "gemini-2.5-flash-preview-05-20")

    url = f"{GEMINI_NATIVE_BASE}/{gemini_model}:generateContent?key={api_key}"

    payload = json.dumps({
        "system_instruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {"role": "user", "parts": [{"text": user_message}]}
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_tokens,
        },
    }).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gemini API HTTP {exc.code} for '{module_name}': {body[:300]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Gemini API connection error for '{module_name}': {exc.reason}") from exc
    except TimeoutError as exc:
        raise RuntimeError(f"Gemini API timed out after {DEFAULT_TIMEOUT}s for '{module_name}'") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Gemini API returned non-JSON for '{module_name}'") from exc

    # Gemini native response format
    try:
        content = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError):
        raise RuntimeError(f"Gemini API returned unexpected format for '{module_name}': {str(data)[:200]}")

    if not content:
        raise RuntimeError(f"Gemini API returned empty content for '{module_name}'")

    content = _strip_code_fences(content)

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Gemini response for '{module_name}' was not valid JSON: {content[:200]}"
        ) from exc


def _call_openai_compatible(
    api_key: str,
    base_url: str,
    model: str,
    module_name: str,
    system_prompt: str,
    user_message: str,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    """Call any OpenAI-compatible /chat/completions endpoint."""
    url = f"{base_url}/chat/completions"

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
        raise RuntimeError(f"API HTTP {exc.code} for '{module_name}': {body[:300]}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"API connection error for '{module_name}': {exc.reason}") from exc
    except TimeoutError as exc:
        raise RuntimeError(f"API timed out after {DEFAULT_TIMEOUT}s for '{module_name}'") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"API returned non-JSON for '{module_name}'") from exc

    content = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
    if not content:
        raise RuntimeError(f"API returned empty content for '{module_name}'")

    content = _strip_code_fences(content)

    try:
        return json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"API response for '{module_name}' was not valid JSON: {content[:200]}"
        ) from exc


def _call_once(
    api_key: str,
    base_url: str,
    model: str,
    module_name: str,
    system_prompt: str,
    user_message: str,
    temperature: float,
    max_tokens: int,
) -> dict[str, Any]:
    """Route to Gemini native or OpenAI-compatible based on key format."""
    if not api_key:
        raise RuntimeError(f"No API key provided for module '{module_name}'.")

    if _is_gemini_native_key(api_key):
        return _call_gemini_native(api_key, model, module_name, system_prompt, user_message, temperature, max_tokens)

    return _call_openai_compatible(api_key, base_url, model, module_name, system_prompt, user_message, temperature, max_tokens)


def call_ai(
    module_name: str,
    system_prompt: str,
    user_message: str,
    temperature: float = 0.3,
    max_tokens: int = 2000,
    api_key: str = "",
    backup_api_key: str = "",
    base_url: str = "",
    model: str = "",
) -> dict[str, Any]:
    """Call AI with primary key first, backup on failure.

    Automatically routes AQ. keys to Gemini native API.
    All other keys use OpenAI-compatible /chat/completions endpoint.
    """
    cfg = _resolve_config(module_name, api_key, backup_api_key, base_url, model)
    primary_err = None

    if cfg["api_key"]:
        try:
            return _call_once(cfg["api_key"], cfg["base_url"], cfg["model"], module_name, system_prompt, user_message, temperature, max_tokens)
        except RuntimeError as exc:
            primary_err = exc
            if not cfg["backup_api_key"]:
                raise RuntimeError(f"API key failed for '{module_name}': {exc}") from exc

    if cfg["backup_api_key"]:
        try:
            return _call_once(cfg["backup_api_key"], cfg["base_url"], cfg["model"], module_name, system_prompt, user_message, temperature, max_tokens)
        except RuntimeError as backup_err:
            raise RuntimeError(
                f"Both API keys failed for '{module_name}'. "
                f"Primary: {primary_err or 'not set'}. Backup: {backup_err}"
            ) from backup_err

    raise RuntimeError(
        f"No API key configured for '{module_name}'. "
        "Please add your API key in your candidate profile."
    )


def is_ai_configured(module_name: str, api_key: str = "", backup_api_key: str = "") -> bool:
    cfg = _resolve_config(module_name, api_key, backup_api_key)
    return bool(cfg["api_key"] or cfg["backup_api_key"])
