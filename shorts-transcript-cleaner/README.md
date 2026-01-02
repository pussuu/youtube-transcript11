# Shorts Transcript Cleaner Website

This document is a **plan** for building a small web app that:

- Lets you paste a **YouTube channel URL**.
- Automatically finds all **YouTube Shorts** on that channel.
- Fetches the **transcript** for each Short 
- If manual captions do NOT exist, automatically fall back to: auto-generated captions
- Cleans the transcript (no timestamps, no noisy formatting).
- Shows the result in order as:
  - `Transcript 1: (HERE TRANSCRIPT)`
  - `Transcript 2: (HERE TRANSCRIPT)`
  - `Transcript 3: (HERE TRANSCRIPT)`
  - ...

This document started as a **plan**, but the core app is now implemented in the `app/` folder.

---

## 1. High-Level Requirements

1. Input: A valid YouTube channel URL (e.g. `https://www.youtube.com/@channelName` or `https://www.youtube.com/channel/CHANNEL_ID`).
2. Backend should:
   - Resolve the channel ID from the URL.
   - Discover all **Shorts videos** on that channel.
   - For each Short, get its transcript
   - If manual captions do NOT exist, automatically fall back to:auto-generated captions
   - Clean and normalize each transcript.
   - Sort Shorts consistently (e.g. **oldest → newest** or **newest → oldest**) before numbering.
3. Frontend should:
   - Have a single page with a text box + button for pasting the channel URL.
   - Show progress / loading state while transcripts are being fetched.
   - Render final output as a simple list: `Transcript 1: ...`, `Transcript 2: ...`, etc.
4. Output format:
   - Plain text, easy to copy.
   - No timestamps, no speaker labels, minimal extra whitespace.
   - Each transcript clearly separated.

---

## 2. Proposed Tech Stack

You can change this later; this is a reasonable starting point.

- **Backend language**: Python
- **Web framework**: FastAPI (simple, fast, async-friendly)
- **Frontend**: Very simple HTML/CSS/JavaScript rendered by the backend (no heavy framework necessary at first)
- **HTTP server**: Uvicorn (for running FastAPI)
- **YouTube integration**:
  - `yt-dlp` (Python library) for discovering Shorts from a channel (no Google API key needed).
  - `youtube-transcript-api` Python library (or direct caption fetching) for transcript extraction.

---

## 3. YouTube Shorts Discovery Design

### 3.1. Extracting Channel ID

1. User pastes a channel URL.
2. Backend parses the URL and handles main patterns:
   - `https://www.youtube.com/@handle`
   - `https://www.youtube.com/channel/CHANNEL_ID`
   - `https://www.youtube.com/c/CustomName`
3. Use `yt-dlp` to resolve the channel URL and access the channel's **Shorts feed** (e.g. by appending `/shorts`).

### 3.2. Listing Shorts Videos

Shorts are just normal videos with **short duration** and usually vertical format. Plan:

1. Use `yt-dlp` against the channel's `/shorts` URL to list entries without downloading video content.
2. Collect for each Short:
   - `videoId`
   - `title`
   - `upload_date` (used as `publishedAt`)
4. Sort the list of Shorts by `publishedAt`.
   - Decide: **oldest first** so numbering matches time order.
   - Then, `Transcript 1` = the oldest Short, `Transcript 2` = next, etc.

### 3.3. Limits / Edge Cases

- Some channels have **no Shorts** → show a clear message.
- Some Shorts do not have transcripts/captions → skip them but list which ones were skipped, or show `Transcript N: (No transcript available)`.
- API quota limits → show an error message if quota is exceeded.

---

## 4. Transcript Fetching & Cleaning Design

### 4.1. Fetching Transcripts

For each `videoId` from the Shorts list:

1. Try to use `youtube-transcript-api` library (or similar) to fetch transcript:
   - Prefer the language requested (default: English) or the first available transcript.
2. If fetching fails (no transcript, disabled, etc.), mark that video as **no transcript available**.

### 4.2. Cleaning Rules

Raw transcripts may contain timestamps like `00:01`, `[0:02]`, `00:03:15`, or similar. They may also have extra line breaks. Cleaning steps:

1. **Remove timestamps** via regex patterns, for example:
   - `^\s*\d{1,2}:\d{2}\s+` at the start of a line.
   - `\[?\d{1,2}:\d{2}(?::\d{2})?\]?` anywhere in the line.
2. Remove any HTML tags if present (e.g. `<i>`, `<b>`).
3. Normalize whitespace:
   - Convert multiple spaces to a single space.
   - Remove leading/trailing spaces.
   - Optionally keep short paragraphs, but avoid one-word-per-line outputs.
4. Join segments:
   - Join lines into larger paragraphs while keeping some breaks for readability.

### 4.3. Final Transcript Format

For each Short that has a transcript, prepare a final block like:

- `Transcript 1: <cleaned transcript text>`
- `Transcript 2: <cleaned transcript text>`
- ...

Design decisions:

- Use **plain text** only.
- Optionally include the **video title** and link on a separate line:
  - `Transcript 1 (Title: XYZ, URL: https://youtu.be/VIDEO_ID): ...`

---

## 5. Backend API Design (FastAPI)

Planned endpoints:

1. `GET /` – Returns HTML page with a form:
   - Input field: `channel_url`.
   - Submit button: "Generate Transcripts".

2. `POST /generate` (or `POST /api/transcripts` if using AJAX):
   - Request body: `channel_url` (string).
   - Steps inside handler:
     1. Validate URL format.
     2. Resolve channel ID.
     3. Fetch list of Shorts.
     4. For each Short, fetch + clean transcript.
     5. Build an ordered list of transcripts.
   - Response:
     - If using server-side templates: Render HTML with all transcripts.
     - If using JSON: Return array of `{ index, title, url, transcript }`.

3. Optional: `GET /health` for health checks.

---

## 6. Frontend UI Plan

Keep it extremely simple at first.

### 6.1. Layout

- Header: "YouTube Shorts Transcript Cleaner".
- Single form:
  - Text input for channel URL.
  - Optional dropdown: language preference.
  - Submit button.
- Area for messages:
  - Errors (invalid URL, no Shorts, no transcripts, API error).
  - Loading indicator.
- Results section:
  - Each transcript rendered as:
    - Heading: `Transcript N` (and maybe video title).
    - Paragraph: cleaned transcript text.

### 6.2. Styling

- Basic CSS (no framework needed initially).
- Ensure transcripts are in a scrollable container so large outputs dont break the page.

---

## 7. Configuration & Secrets

- Use a config file or environment variables for:
  - Maximum number of Shorts per request (e.g. `MAX_SHORTS=200`).
- No Google API key is required when using `yt-dlp`.
- Never hard-code secrets in the code or commit them to version control.

---

## 8. Implementation Steps (Rough Roadmap)

1. **Project setup**
   - Initialize Python virtual environment.
   - Add dependencies: `fastapi`, `uvicorn`, `requests`, `youtube-transcript-api`, etc.
2. **YouTube Shorts client**
   - Implement helper functions to:
     - Normalize channel URLs.
     - Use `yt-dlp` to list Shorts videos from the channel's `/shorts` feed.
3. **Transcript service**
   - Implement a service that, given a `videoId`, returns a **cleaned transcript** or a clear error/`None`.
4. **Core logic**
   - Implement orchestration: from `channel_url` to ordered transcripts list.
5. **API endpoints**
   - Implement `GET /` and `POST /generate`.
6. **UI template**
   - Create a minimal HTML template that calls the backend and displays transcripts.
7. **Testing**
   - Test with multiple real channels (with Shorts and without).
   - Check how it behaves when some Shorts lack transcripts.
8. **Polish**
   - Better error messages.
   - Optional: download transcripts as `.txt` file.

---

## 9. Future Improvements (Optional)

- Allow **per-video selection** instead of always doing all Shorts.
- Support **multiple languages** and automatic language detection.
- Add **rate limiting** or queuing to avoid hitting API quotas.
- Persist results in a small database or cache so repeated runs for the same channel are faster.
- Add authentication if you publish it publicly.
