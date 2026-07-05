# FNT User Guide & Documentation

This guide provides an in-depth tour of the **Founder Note Toolkit (FNT)** features, configuration, and workflows.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [CLI Overview](#cli-overview)
3. [Core Commands](#core-commands)
   - [clip](#clip)
   - [info](#info)
   - [transcript](#transcript)
   - [metadata](#metadata)
   - [search](#search)
   - [viral](#viral)
   - [titles](#titles)
   - [captions](#captions)
4. [Configuration](#configuration)
5. [Troubleshooting & FAQs](#troubleshooting--faqs)

---

## Prerequisites

Before using FNT, ensure your system has the following installed:
* **Python 3.12+**
* **FFmpeg** and **FFprobe** (available in your system `PATH`)
  * **macOS**: `brew install ffmpeg`
  * **Linux (Debian/Ubuntu)**: `sudo apt update && sudo apt install ffmpeg`
  * **Windows**: Download binaries from [ffmpeg.org](https://ffmpeg.org/) and add them to your User Environment Variables.

---

## CLI Overview

Run `fnt --help` to get the list of active commands:
```bash
fnt --help
```

For detailed sub-options, pass `--help` to the subcommand, e.g.:
```bash
fnt clip --help
```

---

## Core Commands

### clip
Downloads a specific section of a YouTube video. It avoids downloading the full video by leveraging `yt-dlp`'s range download options.
```bash
fnt clip --url "https://www.youtube.com/watch?v=..." --start "00:01:00" --end "00:02:15" --name "viral_clip"
```
* **Codec Auto-Conversion**: If yt-dlp retrieves an AV1 stream, FNT automatically transcodes it to H264 (video) and AAC (audio) MP4 format for native support across social platforms.
* **Storage Location**: Saved under `~/Downloads/FounderNote/<Episode_Name>/clip.mp4`.

### info
Fetches and displays video details alongside stream formats (resolution, codec, estimated size).
```bash
fnt info "https://www.youtube.com/watch?v=..."
```

### transcript
Downloads YouTube transcripts/subtitles (supports auto-generated captions and manual ones) in English, Arabic, and other languages.
```bash
fnt transcript "https://www.youtube.com/watch?v=..." --lang "en,ar" --format "all"
```
Formats saved: `.txt`, `.json`, and `.srt`.

### metadata
Saves video attributes directly into `metadata.json` under the episode folder.
```bash
fnt metadata "https://www.youtube.com/watch?v=..."
```

### search
Locates keywords or phrases inside a downloaded transcript and lists matched timestamps with context snippets.
```bash
fnt search ~/Downloads/FounderNote/My_Episode/transcript.json "algorithm"
```

### viral
Analyzes a downloaded JSON transcript to detect the top 3 high-impact hooks/viral clips.
```bash
fnt viral ~/Downloads/FounderNote/My_Episode/transcript.json
```
* Uses **Google Gemini** or **OpenAI** (when API keys are provided).
* Falls back to a local heuristic rules engine if no API keys are configured.

### titles
Generates 5 high-converting viral title suggestions for a specific clip range using AI.
```bash
fnt titles ~/Downloads/FounderNote/My_Episode/transcript.json --start "00:01:00" --end "00:02:00"
```

### captions
Burns SRT subtitles directly into the video stream for mobile short-form feeds (Shorts, TikTok, Reels).
```bash
fnt captions ~/Downloads/FounderNote/My_Episode/clip.mp4 ~/Downloads/FounderNote/My_Episode/transcript.srt
```

---

## Configuration

Configurations are stored in `~/.fnt/config.json`. Use the `config` command to view and edit settings.

* **Show Config**:
  ```bash
  fnt config show
  ```
* **Set Config Key**:
  ```bash
  fnt config set preferred_codec "hevc"
  ```
* **Set AI API Keys**:
  ```bash
  fnt config set gemini_api_key "your-gemini-key"
  fnt config set openai_api_key "your-openai-key"
  ```

---

## Troubleshooting & FAQs

**Q: FFmpeg conversion failed or ffprobe command not found.**
* Ensure FFmpeg is installed and added to your system `PATH`. Run `ffmpeg -version` in your terminal to verify.

**Q: Subtitle download failing for Arabic.**
* Not all videos have Arabic captions. FNT falls back to auto-generated subtitles if available, but if the video lacks Arabic audio/text completely, it will raise an error. Ensure the target language is supported by the video.
