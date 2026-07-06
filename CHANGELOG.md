# Changelog

All notable changes to the **Founder Note Toolkit (FNT)** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-07-06

### Added
- Created optional dependency extras for `ai` (`google-generativeai`, `openai`), `dev` (linters, testers, formatters), and `full` (combines AI and developer tools).
- Added local validation checks for optional AI packages inside the `viral` and `titles` CLI commands, displaying a user-friendly message on how to install them if missing.
- Added new unit tests verifying CLI startup, optional dependency behaviors, and graceful fallback messages when AI dependencies are not installed.

### Changed
- Refactored `pyproject.toml` to remove AI packages (`google-generativeai`, `openai`) from default dependencies to ensure a lightweight and Termux-friendly installation.
- Replaced `typer[all]` with `typer` in default dependencies to avoid unnecessary dependency installation.
- Updated `requirements.txt` to only include the core lightweight dependencies.
- Refactored `install.sh` to support installation modes (`--ai`, `--dev`, `--full`), output friendly warning messages, and verify python version and post-installation sanity of `yt-dlp`.
- Bumped package version to `1.1.0` in both `pyproject.toml` and `fnt/__init__.py`.

### Fixed
- Fixed a bug in `fnt/commands/viral.py` where a non-existent spinner named `"brain"` caused the command to crash. Changed the spinner to the standard `"dots"`.
- Cleaned up un-sorted/un-formatted imports across files to pass strict Ruff checking.
- Added strict type annotations to local test helper functions to pass strict Mypy checks.

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
