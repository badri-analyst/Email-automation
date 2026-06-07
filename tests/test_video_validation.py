"""Tests for video asset validation."""

from services.candidate_assets.url_utils import UrlNormalizer
from services.candidate_assets.videoAssetValidator import VideoAssetValidator


def test_video_validation_accepts_youtube_and_classifies_demo() -> None:
    """Video validator should normalize and classify YouTube links."""
    video, status = VideoAssetValidator().validate("youtu.be/abc123?utm_source=x", "Portfolio demo")

    assert status == "valid"
    assert video is not None
    assert video.video_url == "https://youtu.be/abc123"
    assert video.video_type == "portfolio demo"


def test_video_validation_rejects_unsupported_host() -> None:
    """Unsupported video hosts should be invalid."""
    video, status = VideoAssetValidator().validate("https://example.com/video")

    assert video is None
    assert status == "invalid"


def test_url_normalization_removes_tracking_parameters() -> None:
    """URL normalizer should remove common tracking params."""
    normalized = UrlNormalizer().normalize("https://example.com//portfolio/?utm_campaign=x&id=123")

    assert normalized == "https://example.com/portfolio?id=123"
