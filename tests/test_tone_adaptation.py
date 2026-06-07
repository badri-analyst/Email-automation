"""Tests for tone adaptation."""

from services.email_personalization.toneAdapterService import ToneAdapterService


def test_tone_adapter_uses_personality_guidance() -> None:
    """Tone adapter should map upstream communication tone to allowed email tone."""
    payload = {"personality_context": {"communication_style": {"tone": "Technical"}}}

    assert ToneAdapterService().select_tone(payload) == "technical"
