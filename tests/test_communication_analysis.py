"""Tests for professional communication analysis."""

from services.personality_analysis.communicationStyleAnalyzer import CommunicationStyleAnalyzer


def test_communication_tone_and_structure_extraction() -> None:
    """Analyzer should extract deterministic communication categories."""
    text = (
        "This engineering guide explains API architecture with data analysis. "
        "First, map the workflow. Second, measure outcomes for customers."
    )

    result = CommunicationStyleAnalyzer().analyze(text)

    assert result.tone == "Technical"
    assert result.structure in {"Data-heavy", "Educational", "Practical", "Long-form"}
    assert result.evidence != "Insufficient data."


def test_communication_analysis_returns_insufficient_data_for_weak_text() -> None:
    """Weak evidence should not produce style claims."""
    result = CommunicationStyleAnalyzer().analyze("short")

    assert result.tone == "Insufficient data"
    assert result.evidence == "Insufficient data."
