"""Tests for proof snippet generation."""

from services.candidate_assets.proofSnippetBuilder import ProofSnippetBuilder


def test_proof_snippets_use_candidate_provided_points() -> None:
    """Proof snippets should be factual cleaned versions of provided points."""
    snippets, manual_review = ProofSnippetBuilder().build(
        ["workflow prioritization example", "requirements clarification example"]
    )

    assert snippets == ["workflow prioritization example", "requirements clarification example"]
    assert manual_review is False


def test_proof_snippets_flag_risky_metric_claims() -> None:
    """Metric-like claims should be flagged for manual review."""
    snippets, manual_review = ProofSnippetBuilder().build(["increased delivery by 50%"])

    assert snippets == ["increased delivery by 50%"]
    assert manual_review is True
