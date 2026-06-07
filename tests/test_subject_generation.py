"""Tests for subject line generation."""

from services.email_personalization.subjectLineGenerator import SubjectLineGenerator
from services.email_personalization.subjectSignalMapper import SubjectSignalMapper


def test_subject_line_under_eight_words() -> None:
    """Subject generator should keep output mobile-friendly."""
    subject, subject_type = SubjectLineGenerator().generate("observation_company", "Very Long Company Name Incorporated")

    assert len(subject.split()) <= 8
    assert subject_type == "observation + company"


def test_subject_signal_mapper_prefers_hiring_signal() -> None:
    """Hiring/growth context should map to hiring signal formula."""
    payload = {"company_context": {"growth_or_hiring_signal": "Hiring analysts."}}

    assert SubjectSignalMapper().select_subject_type(payload) == "hiring_signal"
