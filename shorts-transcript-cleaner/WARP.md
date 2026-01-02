## Primary Task for Warp

You are required to generate the initial working version of this project.

### Goal
Build a web application that automatically extracts and cleans transcripts from **all YouTube Shorts of a given channel**.

The user should paste a **YouTube Channel URL**, and the app should:
1. Detect all Shorts on that channel
2. Extract transcripts for each Short
3. Clean the transcripts
4. Display them in ordered, readable format
5. Allow downloading the results

---

### Functional Requirements

#### Input
- A single input field where the user pastes a **YouTube Channel URL**

#### Processing
- Identify all videos that are **YouTube Shorts**
- For each Short:
  - Fetch transcript
  - Prefer **manual captions**
  - Fallback to **auto-generated captions** if manual is unavailable

#### Transcript Cleaning (CRITICAL)
Remove all of the following:
- Timestamps
- WEBVTT metadata
- Alignment/position data
- Repeated lines
- `[music]`, `[Music]`
- `[applause]`
- `[ __ ]`
- Any empty or noise-only lines

The output should be **plain spoken text only**, like a readable paragraph.

#### Output Format
Display transcripts in order like this:

Transcript 1:
<clean transcript text>

Transcript 2:
<clean transcript text>

Transcript 3:
<clean transcript text>

No timestamps. No markers. No metadata.

---

### UI Requirements
- Simple, clean web UI
- Components:
  - Channel URL input
  - “Generate Transcripts” button
  - Scrollable transcript output area
  - “Download as .txt” button
- Support **batch processing** automatically (all Shorts)

---

### Download Requirement
- Allow downloading **all transcripts** as a single `.txt` file
- Preserve numbering order in the file

---

### Tech Constraints
- Choose a modern, simple stack (e.g. Node.js or Python)
- Prefer open-source tools:
  - `yt-dlp` for Shorts detection
  - `youtube-transcript-api` for transcripts
- No paid APIs

---

### Deliverables
Warp should:
1. Generate all necessary source code
2. Create a minimal project structure
3. Provide clear instructions on how to run the app locally

DO NOT stop at planning. Produce working code.
