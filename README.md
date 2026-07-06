# Founder Note Toolkit (FNT) 🎥🔥

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)

**Founder Note Toolkit (FNT)** is a production-ready, clean-architecture CLI toolkit built in Python to help content creators, editors, and founders rapidly extract viral shorts, reels, and TikTok content from long-form YouTube videos. 

FNT lets you download specific clips, extract and format transcripts, analyze speech for high-virality hooks (via Gemini/OpenAI or local heuristics), generate short-form titles, and burn subtitles directly into your MP4 videos.

---

## Key Features

1. **Precision Clipper (`fnt clip`)**: Downloads only the selected start/end range using `yt-dlp` instead of downloading the entire video.
2. **Codec Transcoding (`fnt convert`)**: Auto-detects codecs and transcodes AV1 or other incompatible streams directly into a clean H264/AAC MP4.
3. **Structured Storage Layout**: Organizes downloaded files into a clean folder hierarchy:
   ```
   Downloads/FounderNote/<Episode_Name>/
   ├── clip.mp4
   ├── transcript.txt
   ├── transcript.json
   ├── transcript.srt
   ├── metadata.json
   └── thumbnail.jpg
   ```
4. **Metadata Scraper (`fnt metadata` & `fnt info`)**: Fetches full video info (views, upload date, channels, formats, and codecs) and serializes it to `metadata.json`.
5. **Multi-Format Subtitle Engine (`fnt transcript`)**: Downloads English, Arabic, and auto-generated transcripts, converting WebVTT into clean TXT, JSON, and SRT.
6. **Smart Transcript Search (`fnt search`)**: Instant keyword search showing timestamps and line context.
7. **Viral Segment Analysis (`fnt viral`)**: Identifies high-virality short-form segments using Google Gemini, OpenAI, or a local rule-based heuristic fallback engine.
8. **Viral Titles Generator (`fnt titles`)**: Produces 5 psychology-backed viral title hooks for any given video range.
9. **Caption Burner (`fnt captions`)**: Hard-codes SRT subtitles onto video files using FFmpeg filters.
10. **Rich Terminal UI**: Beautiful progress bars, tables, icons, and status updates styled with `Rich`.

---

## Installation

FNT is designed to be extremely lightweight by default. It can be installed as a bare-minimum core package or with optional dependency groups depending on your requirements (ideal for resource-constrained platforms like Termux).

### System Dependencies
FNT requires **FFmpeg** to extract clips, burn captions, and transcode video.
* **macOS**: `brew install ffmpeg`
* **Ubuntu/Debian**: `sudo apt update && sudo apt install ffmpeg`
* **Windows**: Install via `winget install Gyan.FFmpeg` or download from official sources and add to PATH.
* **Termux (Android)**: `pkg install ffmpeg`

### 1. Installation via pip

You can install FNT using different target options:

* **Core installation** (Default, lightweight, no Rust/C++ compilation required):
  ```bash
  pip install founder-note-toolkit
  ```
* **AI installation** (Adds OpenAI and Google Gemini support):
  ```bash
  pip install "founder-note-toolkit[ai]"
  ```
* **Developer installation** (Adds test and linting suites):
  ```bash
  pip install "founder-note-toolkit[dev]"
  ```
* **Full installation** (Includes all AI and developer dependencies):
  ```bash
  pip install "founder-note-toolkit[full]"
  ```

### 2. Automatic Script Installation

Use the provided installer script `install.sh` to automatically set up a virtual environment and install FNT. The script supports flags matching the pip installation modes:

```bash
chmod +x install.sh

# Install core package (default)
./install.sh

# Install with AI extras
./install.sh --ai

# Install with development tools
./install.sh --dev

# Install with everything
./install.sh --full
```

### 3. Manual Source Installation

1. **Clone the repository and enter the directory**:
   ```bash
   git clone https://github.com/mohamdbidier/founder-note-toolkit.git
   cd founder-note-toolkit
   ```
2. **Setup a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. **Install with desired options**:
   ```bash
   # Core
   pip install -e .
   # Or with AI
   pip install -e .[ai]
   # Or Full
   pip install -e .[full]
   ```

---

## Usage

FNT uses `typer` to expose subcommands. Run the tool using `fnt` (or `python -m fnt.cli`):

```bash
# General help
fnt --help

# 1. Download metadata
fnt metadata "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 2. Get video info & streams
fnt info "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 3. Download transcripts (English and Arabic)
fnt transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --lang "en,ar"

# 4. Search transcripts
fnt search ~/Downloads/FounderNote/Rick_Astley/transcript.json "never"

# 5. Suggest viral segments
fnt viral ~/Downloads/FounderNote/Rick_Astley/transcript.json

# 6. Generate viral title options
fnt titles ~/Downloads/FounderNote/Rick_Astley/transcript.json --start "00:00:10" --end "00:00:40"

# 7. Download a 30s clip (Interactive prompts if options are missing)
fnt clip --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --start "00:00:10" --end "00:00:40" --name "rick_clip"

# 8. Burn subtitles into the clip
fnt captions ~/Downloads/FounderNote/Rick_Astley/rick_clip.mp4 ~/Downloads/FounderNote/Rick_Astley/transcript_en.srt

# 9. Convert arbitrary video files
fnt convert my_input.mov -o converted_output.mp4
```

---

## Configuration

Configurations are stored in `~/.fnt/config.json`. You can manage settings via:

```bash
# Show current config
fnt config show

# Set download directory
fnt config set download_folder "/path/to/downloads"

# Set API Keys for Gemini/OpenAI viral analysis
fnt config set gemini_api_key "AIzaSy..."
fnt config set openai_api_key "sk-proj-..."
```

---

## Architecture & Code Quality

FNT is developed adhering to:
* **Clean Architecture**: Decoupled commands (CLI Controller) from the Business Logic (Services) and Domain Data (Pydantic Models).
* **SOLID Principles**: Single Responsibility Services (e.g. `FFmpegService`, `YoutubeService`, `MetadataService`).
* **Type Hints**: Fully-typed codebase conforming to `mypy` strict configurations.
* **Testing**: Comprehensive unit tests covering business rules and CLI bindings.

Run tests using:
```bash
pytest --cov=fnt tests/
```

---

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned future features and updates.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
