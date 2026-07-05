"""AI Analysis Service for FNT.

Interacts with Google Gemini and OpenAI to find viral hooks, generate titles, and segment clips.
"""

import json
import os
import re
from typing import Any

from fnt.config import load_config
from fnt.models import TitleSuggestion, Transcript, ViralSegment
from fnt.services.utils import format_timestamp
from fnt.settings import get_logger


class AIService:
    """Manages AI analysis tasks using Gemini, OpenAI, or local rules engine fallback."""

    def __init__(self) -> None:
        self.logger = get_logger()
        config = load_config()
        self.gemini_key = config.gemini_api_key or os.getenv("GEMINI_API_KEY")
        self.openai_key = config.openai_api_key or os.getenv("OPENAI_API_KEY")

        # Lazy imports for clients
        self._gemini_client: Any = None
        self._openai_client: Any = None

    def _get_gemini_client(self) -> Any | None:
        """Lazy load and construct Gemini client."""
        if not self.gemini_key:
            return None
        if self._gemini_client is None:
            try:
                import google.generativeai as genai

                genai.configure(api_key=self.gemini_key)  # type: ignore[attr-defined]
                self._gemini_client = genai.GenerativeModel("gemini-1.5-flash")  # type: ignore[attr-defined]
                self.logger.info("Gemini AI client successfully initialized.")
            except Exception as e:
                self.logger.error("Failed to initialize Gemini client: %s", e)
        return self._gemini_client

    def _get_openai_client(self) -> Any | None:
        """Lazy load and construct OpenAI client."""
        if not self.openai_key:
            return None
        if self._openai_client is None:
            try:
                from openai import OpenAI

                self._openai_client = OpenAI(api_key=self.openai_key)
                self.logger.info("OpenAI client successfully initialized.")
            except Exception as e:
                self.logger.error("Failed to initialize OpenAI client: %s", e)
        return self._openai_client

    def analyze_viral_segments(self, transcript: Transcript) -> list[ViralSegment]:
        """Analyze transcripts to detect viral segments using Gemini, OpenAI, or a fallback engine."""
        if not transcript.segments:
            return []

        # Check for Gemini
        gemini_model = self._get_gemini_client()
        if gemini_model:
            try:
                return self._gemini_analyze_viral(transcript, gemini_model)
            except Exception as e:
                self.logger.warning("Gemini viral analysis failed, trying fallback: %s", e)

        # Check for OpenAI
        openai_client = self._get_openai_client()
        if openai_client:
            try:
                return self._openai_analyze_viral(transcript, openai_client)
            except Exception as e:
                self.logger.warning("OpenAI viral analysis failed, trying fallback: %s", e)

        # Fallback to rules engine
        self.logger.info(
            "No AI credentials available or API failed. Running rules-based segment extractor."
        )
        return self._fallback_analyze_viral(transcript)

    def generate_viral_titles(self, clip_text: str) -> list[TitleSuggestion]:
        """Generate a list of high-converting titles for a short clip."""
        if not clip_text:
            return []

        gemini_model = self._get_gemini_client()
        if gemini_model:
            try:
                return self._gemini_generate_titles(clip_text, gemini_model)
            except Exception as e:
                self.logger.warning("Gemini title generation failed: %s", e)

        openai_client = self._get_openai_client()
        if openai_client:
            try:
                return self._openai_generate_titles(clip_text, openai_client)
            except Exception as e:
                self.logger.warning("OpenAI title generation failed: %s", e)

        # Fallback
        return self._fallback_generate_titles(clip_text)

    # --- GEMINI IMPLEMENTATIONS ---
    def _gemini_analyze_viral(self, transcript: Transcript, model: Any) -> list[ViralSegment]:
        prompt = self._build_viral_prompt(transcript)
        response = model.generate_content(
            prompt, generation_config={"response_mime_type": "application/json"}
        )
        return self._parse_viral_json(response.text)

    def _gemini_generate_titles(self, clip_text: str, model: Any) -> list[TitleSuggestion]:
        prompt = self._build_title_prompt(clip_text)
        response = model.generate_content(
            prompt, generation_config={"response_mime_type": "application/json"}
        )
        return self._parse_title_json(response.text)

    # --- OPENAI IMPLEMENTATIONS ---
    def _openai_analyze_viral(self, transcript: Transcript, client: Any) -> list[ViralSegment]:
        prompt = self._build_viral_prompt(transcript)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a viral YouTube short-form content producer. Return only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return self._parse_viral_json(content)

    def _openai_generate_titles(self, clip_text: str, client: Any) -> list[TitleSuggestion]:
        prompt = self._build_title_prompt(clip_text)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional copywriter and short-form titles expert. Return only valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return self._parse_title_json(content)

    # --- PROMPT BUILDERS ---
    def _build_viral_prompt(self, transcript: Transcript) -> str:
        transcript_data = []
        for s in transcript.segments[:150]:  # Limit transcript to keep prompt context size safe
            transcript_data.append(f"[{format_timestamp(s.start)}] {s.text}")

        transcript_str = "\n".join(transcript_data)

        return f"""
Analyze the following transcript of a video to identify exactly 3 high-impact, potentially viral segments suitable for short-form clips (TikTok, YouTube Shorts, Reels).
A good short-form clip contains a complete hook, an explanation/story, and a resolution. It should be between 30 and 90 seconds.

Transcript:
{transcript_str}

Respond ONLY with a JSON object in this format:
{{
  "segments": [
    {{
      "start_time": "hh:mm:ss",
      "end_time": "hh:mm:ss",
      "title": "Viral Hook Title",
      "hook": "What is the hook at the start",
      "reason": "Why this segment has high virality potential",
      "score": 95
    }}
  ]
}}
"""

    def _build_title_prompt(self, clip_text: str) -> str:
        return f"""
Generate 5 viral short-form video titles for a clip with the following transcript content.
Focus on curiosity gaps, shock factor, emotional hooks, or clear contrast.

Clip Transcript Content:
{clip_text}

Respond ONLY with a JSON object in this format:
{{
  "titles": [
    {{
      "title": "The Title text",
      "hook_type": "Curiosity/Shock/Question/Contrast",
      "description": "Brief reason why this title will perform well"
    }}
  ]
}}
"""

    # --- JSON PARSERS ---
    def _parse_viral_json(self, raw_text: str) -> list[ViralSegment]:
        cleaned = self._clean_json_markdown(raw_text)
        data = json.loads(cleaned)
        segments = data.get("segments", [])
        return [ViralSegment(**s) for s in segments]

    def _parse_title_json(self, raw_text: str) -> list[TitleSuggestion]:
        cleaned = self._clean_json_markdown(raw_text)
        data = json.loads(cleaned)
        titles = data.get("titles", [])
        return [TitleSuggestion(**t) for t in titles]

    def _clean_json_markdown(self, text: str) -> str:
        """Strip markdown fence formatting blocks if present in AI output."""
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(json)?\n", "", text)
            text = re.sub(r"\n```$", "", text)
        return text.strip()

    # --- RULE ENGINE FALLBACKS ---
    def _fallback_analyze_viral(self, transcript: Transcript) -> list[ViralSegment]:
        """Rules-based fallback when AI keys are unavailable.

        Finds segments containing high-value keyphrases, questions, or just divides the transcript evenly.
        """
        segments = transcript.segments
        total_segs = len(segments)
        if total_segs < 5:
            # Just return the entire thing
            start_t = format_timestamp(segments[0].start)
            end_t = format_timestamp(segments[-1].start + segments[-1].duration)
            return [
                ViralSegment(
                    start_time=start_t,
                    end_time=end_t,
                    title="Highlight Clip",
                    hook="Initial segment overview",
                    reason="Fallback hook segment extracted from video start.",
                    score=80,
                )
            ]

        # Look for keywords indicating value/stories
        action_words = [
            "story",
            "secret",
            "lesson",
            "revenue",
            "failed",
            "learned",
            "algorithm",
            "hacks",
            "hired",
        ]
        candidates = []

        # Scan for interest points
        for i in range(1, total_segs - 5):
            chunk = segments[i : i + 6]
            chunk_text = " ".join([c.text for c in chunk]).lower()

            # Rate the chunk
            score = 50
            if "?" in chunk_text:
                score += 15
            for w in action_words:
                if w in chunk_text:
                    score += 10

            # Avoid overlaps by taking steps
            start_sec = chunk[0].start
            end_sec = chunk[-1].start + chunk[-1].duration
            duration = end_sec - start_sec

            if 25 <= duration <= 75:
                candidates.append((score, chunk[0].start, end_sec, chunk_text))

        # Sort by score and grab top 3 non-overlapping
        candidates.sort(key=lambda x: x[0], reverse=True)
        selected: list[tuple[float, float]] = []
        for _score, start, end, _text in candidates:
            # Check overlap with already selected
            overlap = False
            for s_start, s_end in selected:
                if not (end <= s_start or start >= s_end):
                    overlap = True
                    break
            if not overlap:
                selected.append((start, end))
                if len(selected) >= 3:
                    break

        # If we couldn't find enough, grab starting segments
        if len(selected) < 3:
            step = max(1, total_segs // 4)
            for i in range(0, total_segs, step):
                if len(selected) >= 3:
                    break
                sub = segments[i : min(i + 8, total_segs)]
                start = sub[0].start
                end = sub[-1].start + sub[-1].duration
                if (start, end) not in selected:
                    selected.append((start, end))

        results = []
        for idx, (start, end) in enumerate(selected, 1):
            results.append(
                ViralSegment(
                    start_time=format_timestamp(start),
                    end_time=format_timestamp(end),
                    title=f"Viral Segment suggestion #{idx}",
                    hook="Extracted hook matching speech patterns.",
                    reason="Extracted via keyword matching rules (AI Key missing).",
                    score=75 + idx,
                )
            )

        return results

    def _fallback_generate_titles(self, clip_text: str) -> list[TitleSuggestion]:
        """Generate static marketing hook titles when AI keys are unavailable."""
        words = clip_text.split()
        keyword = words[0] if words else "This"
        if len(words) > 2:
            keyword = f"{words[0]} {words[1]} {words[2]}"

        return [
            TitleSuggestion(
                title=f"The Truth About {keyword}!",
                hook_type="Curiosity",
                description="Creates an information gap that forces viewers to stay.",
            ),
            TitleSuggestion(
                title=f"Why 99% Of Creators Fail At {keyword}",
                hook_type="Contrast",
                description="Uses negative bias and high stakes to draw attention.",
            ),
            TitleSuggestion(
                title=f"How We Mastered {keyword} In 24 Hours",
                hook_type="Curiosity",
                description="Implies speed and easy replication of success.",
            ),
            TitleSuggestion(
                title=f"Is {keyword} Finally Dead?",
                hook_type="Shock",
                description="Uses fear-of-missing-out (FOMO) and negative shock values.",
            ),
            TitleSuggestion(
                title=f"The Lazy Way to Do {keyword}",
                hook_type="Curiosity",
                description="Promises low effort and high reward, highly viral.",
            ),
        ]
