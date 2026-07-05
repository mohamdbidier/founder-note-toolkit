"""Tests for FNT utility functions."""

import pytest

from fnt.services.utils import format_timestamp, parse_timestamp, sanitize_filename


def test_parse_timestamp() -> None:
    """Test parsing various timestamp formats to seconds."""
    assert parse_timestamp("120") == 120.0
    assert parse_timestamp("02:00") == 120.0
    assert parse_timestamp("01:00:00") == 3600.0
    assert parse_timestamp("00:01:30,500") == 90.5
    assert parse_timestamp("00:01:30.500") == 90.5

    with pytest.raises(ValueError):
        parse_timestamp("invalid-format")


def test_format_timestamp() -> None:
    """Test formatting float seconds to timestamp strings."""
    assert format_timestamp(120.0) == "00:02:00"
    assert format_timestamp(3690.0) == "01:01:30"
    assert format_timestamp(90.5, include_ms=True) == "00:01:30,500"
    assert format_timestamp(-10.0) == "00:00:00"


def test_sanitize_filename() -> None:
    """Test sanitizing filename strings."""
    assert sanitize_filename("Hello World!") == "Hello_World!"
    assert sanitize_filename("Video/Audio? *:") == "VideoAudio"
