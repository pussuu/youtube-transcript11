import os
from typing import List, Optional

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .youtube_client import get_shorts_for_channel_url
from .transcript_service import build_transcripts_for_videos


app = FastAPI(title="YouTube Shorts Transcript Cleaner")

# Mount static files (CSS, JS, etc.)
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Templates directory
templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
templates = Jinja2Templates(directory=templates_dir)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Render the homepage with the input form."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "error": None,
            "channel_url": "",
            "max_shorts": 50,
            "transcripts": [],
        },
    )


@app.post("/generate", response_class=HTMLResponse)
async def generate_transcripts(
    request: Request,
    channel_url: str = Form(...),
    language: str = Form("en"),
    max_shorts: int = Form(50),
) -> HTMLResponse:
    """Handle form submission: fetch Shorts, get transcripts, render results."""
    error: Optional[str] = None
    transcripts: List[dict] = []

    channel_url = channel_url.strip()
    if not channel_url:
        error = "Please provide a YouTube channel URL."
    else:
        try:
            # Clamp max_shorts to a reasonable range
            if max_shorts <= 0:
                max_shorts = 1
            if max_shorts > 500:
                max_shorts = 500

            videos = get_shorts_for_channel_url(channel_url, max_results=max_shorts)
            if not videos:
                error = "No Shorts videos found for this channel, or the channel could not be resolved."
            else:
                transcripts = build_transcripts_for_videos(videos, language=language)
                if not any(t["has_transcript"] for t in transcripts):
                    error = "No transcripts were found for any Shorts on this channel."
        except Exception as exc:  # broad catch to surface friendly errors
            error = f"An error occurred while processing the channel: {exc}"

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "error": error,
            "channel_url": channel_url,
            "max_shorts": max_shorts,
            "transcripts": transcripts,
        },
    )


@app.post("/download", response_class=PlainTextResponse)
async def download_transcripts(
    channel_url: str = Form(...),
    language: str = Form("en"),
    max_shorts: int = Form(50),
) -> PlainTextResponse:
    """Rebuild transcripts and return them as a downloadable .txt file."""
    channel_url = channel_url.strip()
    if not channel_url:
        content = "No channel URL provided."
        return PlainTextResponse(content=content, status_code=400)

    if max_shorts <= 0:
        max_shorts = 1
    if max_shorts > 500:
        max_shorts = 500

    videos = get_shorts_for_channel_url(channel_url, max_results=max_shorts)
    if not videos:
        content = "No Shorts videos found for this channel, or the channel could not be resolved."
        return PlainTextResponse(content=content, status_code=404)

    transcripts = build_transcripts_for_videos(videos, language=language)

    lines: List[str] = []
    for t in transcripts:
        header = f"Transcript {t['index']}:"
        lines.append(header)
        if t.get("has_transcript") and t.get("transcript"):
            lines.append(t["transcript"])
        else:
            lines.append("No transcript available.")
        lines.append("")  # blank line between transcripts

    content = "\n".join(lines).strip() + "\n"
    headers = {"Content-Disposition": "attachment; filename=shorts_transcripts.txt"}
    return PlainTextResponse(content=content, headers=headers)


@app.get("/health")
async def health() -> dict:
    """Simple health check endpoint."""
    return {"status": "ok"}
