import re
from typing import Dict, List

from youtube_transcript_api import (
    YouTubeTranscriptApi,
    NoTranscriptFound,
    TranscriptsDisabled,
)


class TranscriptError(Exception):
    pass


def _fetch_transcript_segments(video_id: str, language: str = "en") -> List[Dict]:
    """Fetch transcript segments for a video, preferring manual then auto-generated.

    If manual captions in the requested language do NOT exist, automatically
    fall back to auto-generated captions.
    """
    try:
        transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
    except (NoTranscriptFound, TranscriptsDisabled) as exc:
        raise TranscriptError(str(exc)) from exc

    # 1) Try manually created transcript in requested language
    try:
        transcript = transcripts.find_manually_created_transcript([language])
        return transcript.fetch()
    except NoTranscriptFound:
        pass

    # 2) Try auto-generated transcript in requested language
    try:
        transcript = transcripts.find_generated_transcript([language])
        return transcript.fetch()
    except NoTranscriptFound:
        pass

    # 3) Fallback: any available transcript (first one)
    for transcript in transcripts:
        try:
            return transcript.fetch()
        except Exception:
            continue

    raise TranscriptError("No usable transcript found.")


_TIMESTAMP_PATTERN = re.compile(r"\[?\d{1,2}:\d{2}(?::\d{2})?\]?")
_HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
_WHITESPACE_PATTERN = re.compile(r"\s+")
_NOISE_BRACKETS_PATTERN = re.compile(r"\[(?:music|Music|applause|Applause|__)\]")


def clean_transcript_text(raw_text: str) -> str:
    """Clean a raw transcript string: remove timestamps, noise, extra whitespace."""
    text = _TIMESTAMP_PATTERN.sub(" ", raw_text)
    text = _HTML_TAG_PATTERN.sub(" ", text)
    text = _NOISE_BRACKETS_PATTERN.sub(" ", text)
    text = _WHITESPACE_PATTERN.sub(" ", text)
    return text.strip()


def build_transcripts_for_videos(videos: List[Dict], language: str = "en") -> List[Dict]:
    """Given a list of video metadata, return ordered transcript entries.

    Each entry has the shape:
    {
        "index": N,
        "title": str,
        "url": str,
        "transcript": str | None,
        "has_transcript": bool,
        "error": str | None,
    }
    """
    results: List[Dict] = []

    for idx, video in enumerate(videos, start=1):
        video_id = video.get("video_id")
        title = video.get("title") or ""
        url = video.get("url") or ""

        transcript_text: str | None = None
        error: str | None = None

        try:
            segments = _fetch_transcript_segments(video_id, language=language)

            # Join segment texts, skipping empty and repeated lines, then clean
            joined_segments: List[str] = []
            last_line: str | None = None
            for seg in segments:
                line = (seg.get("text", "") or "").strip()
                if not line:
                    continue
                if line == last_line:
                    continue
                last_line = line
                joined_segments.append(line)

            raw_text = " ".join(joined_segments)
            transcript_text = clean_transcript_text(raw_text)
            if not transcript_text:
                error = "Transcript is empty after cleaning."
        except TranscriptError as exc:
            error = str(exc)

        has_transcript = transcript_text is not None and not error

        results.append(
            {
                "index": idx,
                "title": title,
                "url": url,
                "transcript": transcript_text if has_transcript else None,
                "has_transcript": has_transcript,
                "error": error,
            }
        )

    return results
