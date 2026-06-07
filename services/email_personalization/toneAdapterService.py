"""Tone adaptation service."""

from services.email_personalization.rule_loader import load_email_config


class ToneAdapterService:
    """Select allowed tone from communication guidance."""

    def __init__(self) -> None:
        self._rules = load_email_config("tone_rules.json")

    def select_tone(self, payload: dict) -> str:
        """Return deterministic allowed tone."""
        personality = payload.get("personality_context", {})
        raw_tone = personality.get("communication_style", {}).get("tone", "")
        tone = self._rules["tone_map"].get(raw_tone, self._rules["default_tone"])
        return tone if tone in self._rules["allowed_tones"] else self._rules["default_tone"]
