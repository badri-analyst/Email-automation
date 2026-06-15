"""Email quality validation."""


class EmailQualityValidator:
    """Validate subject/body length and CTA constraints."""

    def __init__(self, max_subject_words: int = 10, max_body_words: int = 200) -> None:
        self._max_subject_words = max_subject_words
        self._max_body_words = max_body_words

    def word_count(self, text: str) -> int:
        """Return word count."""
        return len(str(text).split())

    def validate(self, subject: str, body: str) -> tuple[bool, str]:
        """Return quality validation result."""
        if self.word_count(subject) > self._max_subject_words:
            return False, "Subject line exceeds word limit."
        if self.word_count(body) > self._max_body_words:
            return False, "Email body exceeds word limit."
        return True, ""

    def shorten_body(self, body: str) -> str:
        """Shorten body to configured word limit."""
        words = body.split()
        if len(words) <= self._max_body_words:
            return body
        return " ".join(words[: self._max_body_words]).rstrip(" ,;") + "."
