"""Tests for outreach cleaning components."""

from services.cleaning.html_cleaner import HtmlCleaner
from services.cleaning.unicode_cleaner import UnicodeCleaner
from services.cleaning.whitespace_cleaner import WhitespaceCleaner


def test_whitespace_cleaner_trims_and_compresses_spaces() -> None:
    """Whitespace cleaner should trim and collapse repeated whitespace."""
    assert WhitespaceCleaner().clean("  John      Smith  ") == "John Smith"


def test_unicode_cleaner_removes_invisible_characters() -> None:
    """Unicode cleaner should remove zero-width formatting characters."""
    assert UnicodeCleaner().clean("Jo\u200bhn\u200d Smith") == "John Smith"


def test_html_cleaner_removes_tags_and_script_content() -> None:
    """HTML cleaner should remove tags and script/style payloads."""
    cleaned = HtmlCleaner().clean("<div>CEO</div><script>alert('x')</script>")
    assert cleaned.strip() == "CEO"
