"""Tests for outreach inference components."""

from services.inference.department_inference import DepartmentInference
from services.inference.name_splitter import NameSplitter
from services.inference.seniority_inference import SeniorityInference


def test_name_splitter_handles_two_part_and_single_word_names() -> None:
    """Name splitter should make conservative assumptions."""
    splitter = NameSplitter()

    assert splitter.split("John Smith") == ("John", "Smith")
    assert splitter.split("Madonna") == ("Madonna", "")


def test_seniority_inference_uses_keyword_mapping() -> None:
    """Seniority inference should map titles deterministically."""
    inference = SeniorityInference()

    assert inference.infer("Senior Software Engineer") == "senior"
    assert inference.infer("VP Sales") == "executive"


def test_department_inference_uses_keyword_mapping() -> None:
    """Department inference should map titles deterministically."""
    inference = DepartmentInference()

    assert inference.infer("Marketing Manager") == "marketing"
    assert inference.infer("Head of Engineering") == "engineering"
