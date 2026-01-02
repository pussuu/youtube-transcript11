from __future__ import annotations

from typing import List, Dict

import yt_dlp


class ShortsDiscoveryError(Exception):
    pass


def _extract_shorts_url(channel_url: str) -> str:
    """Return a URL that points to the channel's Shorts feed.

    For most channel URL forms, appending "/shorts" is enough, e.g.:
    - https://www.youtube.com/@handle          -> https://www.youtube.com/@handle/shorts
    - https://www.youtube.com/channel/ID       -> https://www.youtube.com/channel/ID/shorts
    - https://www.youtube.com/c/CustomName     -> https://www.youtube.com/c/CustomName/shorts
    """
    url = channel_url.strip()
    if not url:
        raise ShortsDiscoveryError("Empty channel URL.")
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    if url.endswith("/"):
        url = url[:-1]
    return url + "/shorts"


def get_shorts_for_channel_url(channel_url: str, max_results: int = 200) -> List[Dict]:
    """Use yt-dlp to list Shorts videos for a channel URL.

    This does NOT require any API key, and relies only on yt-dlp's extraction
    of the channel's Shorts feed.
    """
    shorts_url = _extract_shorts_url(channel_url)

    ydl_opts = {
        "skip_download": True,
        "ignoreerrors": True,
        "extract_flat": True,  # don't resolve each video fully
        "quiet": True,
    }

    videos: List[Dict] = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(shorts_url, download=False)

    # info may represent a playlist or a single entry
    entries = info.get("entries") if isinstance(info, dict) else None
    if not entries:
        return []

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        video_id = entry.get("id")
        title = entry.get("title") or ""
        upload_date = entry.get("upload_date")  # e.g. "20250103"
        url = entry.get("url") or (f"https://youtu.be/{video_id}" if video_id else None)
        if not video_id or not url:
            continue

        videos.append(
            {
                "video_id": video_id,
                "title": title,
                "published_at": upload_date or "",
                "url": url,
            }
        )
        if len(videos) >= max_results:
            break

    # Sort oldest -> newest by upload_date when present
    videos.sort(key=lambda v: v.get("published_at") or "")
    return videos
