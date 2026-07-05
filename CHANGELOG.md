# Changelog

All notable changes to the **Founder Note Toolkit (FNT)** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-07-05

### Added
- Core Typer CLI structure (`fnt`).
- Interactive clipper command `fnt clip` with `yt-dlp` range downloading, auto-conversion for AV1 streams, and progress bars.
- Metadata scraper command `fnt metadata` to fetch and write structured video data to `metadata.json`.
- Info details command `fnt info` listing video summaries and stream quality tables.
- Subtitles engine `fnt transcript` supporting English, Arabic, and auto-generated VTT conversion to TXT, JSON, and SRT.
- Keyword locator command `fnt search` to scan transcripts and output timestamps.
- AI Analyzer command `fnt viral` predicting viral short-form segments using Gemini / OpenAI or a local rules-based fallback engine.
- Viral title hooks command `fnt titles` producing title options styled by psychology hooks.
- Burner command `fnt captions` applying SRT files directly into video streams using FFmpeg vf filters.
- Converter tool `fnt convert` transcoding legacy movies to standard H264/AAC MP4 formats.
- Configuration controller `fnt config` for managing themes, storage, and API keys.
- Automatic installation script `install.sh` verifying system environments.
- Comprehensive unit test suite covering domain modules and CLI commands.
