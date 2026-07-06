# Developer Task List (TODO)

This document lists codebase tasks, optimizations, and features, prioritized by importance.

---

## 🔴 Critical
* **Windows MAX_PATH & Reserved Device Safety**
  * [x] Enforce filename length restrictions and sanitization for Windows system calls.
* **Corrupted Configurations Protection**
  * [x] Restructure JSON parsing of local config to write defaults if parsing throws exceptions, preventing load failure loops.
* **FFmpeg Path Escaping**
  * [x] Resolve colon/quote/space issues in paths passed to FFmpeg filter graphs.
* **Conversion Validation**
  * [x] Implement post-transcode validation verifying output file existence and non-zero size.

---

## 🟡 Important
* **Package Extra Development Setup**
  * [x] Add `dev` dev-dependencies block to `pyproject.toml` so developers can configure tests and style linters in one step.
* **Local Subtitle Transcriptions (ASR)**
  * [ ] Integrate Whisper (local runtime or API options) to transcribe local files that do not have YouTube subtitles.
* **Dynamic Subtitle Styling**
  * [ ] Provide options to override the burned captions colors, font size, and layout alignment.
* **Verify Windows Command Integrations**
  * [ ] Add automated integration tests in CI/CD pipeline simulating execution on Windows environments.

---

## 🟢 Nice to Have
* **Interactive Timelines Previews**
  * [ ] Show a summary block of the video timestamps and query user confirmation before starting download.
* **Log Rotation Config**
  * [ ] Set up `RotatingFileHandler` limits on `fnt.log` to prevent unbounded log file growth.
* **Web timeline GUI**
  * [ ] Build a local Next.js or Streamlit web dashboard for timeline trimming and subtitle review.
