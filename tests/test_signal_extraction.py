"""Tests for observable signal and motivator extraction."""

from services.personality_analysis.professionalMotivatorExtractor import ProfessionalMotivatorExtractor
from services.personality_analysis.professionalSignalExtractor import ProfessionalSignalExtractor


def test_professional_signal_extraction_requires_evidence() -> None:
    """Signals should be extracted only from observable professional evidence."""
    text = "Delivered data analysis, stakeholder collaboration, and workflow process improvements."

    signals = ProfessionalSignalExtractor().extract(text)

    assert signals
    assert all(signal.evidence for signal in signals)
    assert {signal.signal for signal in signals} & {"Analytical", "Collaborative", "Process-focused"}


def test_professional_motivator_extraction_requires_evidence() -> None:
    """Motivators should be extracted only from observable evidence."""
    text = "Focused on customer value, efficiency, process improvement, and delivery quality."

    motivators = ProfessionalMotivatorExtractor().extract(text)

    assert motivators
    assert all(motivator.evidence for motivator in motivators)
    assert {motivator.motivator for motivator in motivators} & {
        "Customer value",
        "Efficiency / process improvement",
        "Delivery excellence",
    }
