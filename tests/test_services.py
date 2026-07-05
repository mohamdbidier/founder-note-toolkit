"""Tests for FNT services (ConverterService and TranscriptService)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from fnt.models import Transcript, TranscriptItem
from fnt.services.converter import ConverterService
from fnt.services.transcript import TranscriptService


def test_converter_service_skip(tmp_path: Path) -> None:
    """Test ConverterService skips conversion when codecs match H264/AAC."""
    mock_ffmpeg = MagicMock()
    mock_ffmpeg.is_installed.return_value = True
    # Mock video as already H264 and audio as AAC
    mock_ffmpeg.detect_codecs.return_value = {"video": "h264", "audio": "aac"}

    input_file = tmp_path / "input.mp4"
    output_file = tmp_path / "output.mp4"
    input_file.touch()

    service = ConverterService(ffmpeg_service=mock_ffmpeg)

    # Run conversion (it should copy files instead of transcoding)
    with patch("shutil.copy2") as mock_copy:
        converted = service.convert_video(input_file, output_file, force=False)
        assert not converted
        mock_copy.assert_called_once_with(input_file, output_file)
        mock_ffmpeg.convert_to_h264_aac.assert_not_called()


def test_converter_service_transcode(tmp_path: Path) -> None:
    """Test ConverterService executes transcode when codecs differ."""
    mock_ffmpeg = MagicMock()
    mock_ffmpeg.is_installed.return_value = True
    mock_ffmpeg.detect_codecs.return_value = {"video": "vp9", "audio": "opus"}

    input_file = tmp_path / "input.webm"
    output_file = tmp_path / "output.mp4"
    input_file.touch()

    service = ConverterService(ffmpeg_service=mock_ffmpeg)

    converted = service.convert_video(input_file, output_file, force=False)
    assert converted
    mock_ffmpeg.convert_to_h264_aac.assert_called_once_with(input_file, output_file)


def test_transcript_service_save_formats(tmp_path: Path) -> None:
    """Test saving transcripts to TXT, JSON, and SRT formats."""
    service = TranscriptService()

    segments = [
        TranscriptItem(text="Hello", start=0.0, duration=2.5),
        TranscriptItem(text="World", start=3.0, duration=1.5),
    ]
    transcript = Transcript(
        video_id="test_id",
        language="en",
        is_auto_generated=False,
        segments=segments,
    )

    txt_path = tmp_path / "transcript.txt"
    json_path = tmp_path / "transcript.json"
    srt_path = tmp_path / "transcript.srt"

    service.save_as_txt(transcript, txt_path)
    service.save_as_json(transcript, json_path)
    service.save_as_srt(transcript, srt_path)

    assert txt_path.exists()
    assert json_path.exists()
    assert srt_path.exists()

    # Verify SRT format
    srt_content = srt_path.read_text(encoding="utf-8")
    assert "1" in srt_content
    assert "00:00:00,000 --> 00:00:02,500" in srt_content
    assert "Hello" in srt_content
    assert "2" in srt_content
    assert "00:00:03,000 --> 00:00:04,500" in srt_content
    assert "World" in srt_content
