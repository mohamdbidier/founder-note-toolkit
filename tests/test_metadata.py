"""Tests for metadata serialization and persistence."""

from pathlib import Path

from fnt.models import VideoMetadata
from fnt.services.metadata import MetadataService


def test_save_and_load_metadata(tmp_path: Path) -> None:
    """Test saving and loading metadata JSON records."""
    service = MetadataService()

    meta = VideoMetadata(
        title="Test Title",
        url="https://youtube.com/watch?v=12345",
        duration=300,
        channel="Test Channel",
        views=1500,
        upload_date="20260705",
        description="A test description.",
        thumbnail_url="https://example.com/thumb.jpg",
        formats=[],
    )

    file_path = tmp_path / "metadata.json"
    service.save_metadata(meta, file_path)

    assert file_path.exists()

    loaded = service.load_metadata(file_path)
    assert loaded.title == meta.title
    assert loaded.url == meta.url
    assert loaded.duration == meta.duration
    assert loaded.channel == meta.channel
    assert loaded.views == meta.views
    assert loaded.upload_date == meta.upload_date
    assert loaded.description == meta.description
