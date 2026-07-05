# FNT Developer Task List (TODO)

This list tracks active tasks, bug fixes, refactoring goals, and low-level improvements.

---

## 🚀 High Priority (Bug Fixes & CLI Optimizations)
- [ ] **Enhanced Subtitle Parsing Exceptions**:
  - [ ] Write robust fallbacks for malformed VTT files missing standard line structures.
- [ ] **FFmpeg Path Resolver**:
  - [ ] Add explicit windows path-escaping helper methods to ensure `burn_subtitles` works flawlessly across Windows directories with whitespace.
- [ ] **yt-dlp Option Tuning**:
  - [ ] Add options to limit bandwidth or specify download speeds for large clips.

---

## 🛠️ Medium Priority (Refactoring & Code Quality)
- [ ] **Expand Test Coverage**:
  - [ ] Add mock tests for `fnt/services/youtube.py` downloading routines.
  - [ ] Add mock tests for `fnt/services/ffmpeg.py` shell commands and error returns.
  - [ ] Add unit tests for `convert` command execution.
- [ ] **Strict Typing Compliance**:
  - [ ] Resolve any remaining `mypy` strict type-checking issues (e.g. untyped third-party libraries).
- [ ] **Better Logger Rotation**:
  - [ ] Configure `RotatingFileHandler` in `fnt/settings.py` to prevent logs from growing indefinitely.

---

## 💡 Low Priority (User Experience & Convenience)
- [ ] **Theme Customization**:
  - [ ] Expand theme support so users can customize specific colors for warnings, success tables, and prompts.
- [ ] **Interactive Clip Confirmation**:
  - [ ] Show a summary table of the segment to download and request a Y/n confirmation before starting download.
