"""Tone adaptation service."""

from services.email_personalization.rule_loader import load_email_config


class ToneAdapterService:
    """Select tone from tone_guidance in FinalPersonalizationPayload."""

    def __init__(self) -> None:
        self._rules = load_email_config("tone_rules.json")

    def select_tone(self, payload: dict) -> str:
        tone_guidance = str(payload.get("tone_guidance") or "").lower()
        allowed = self._rules.get("allowed_tones", [])
        default = self._rules.get("default_tone", "professional")

        for tone in allowed:
            if tone in tone_guidance:
                return tone
        return default
