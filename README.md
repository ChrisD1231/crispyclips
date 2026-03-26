# 🎬 CrispyClips

CrispyClips is a powerful, local-first AI YouTube Clipping tool designed to autonomously transform long-form YouTube videos into highly engaging, viral-ready short-form content. 

Operating entirely from your local machine, CrispyClips utilizes state-of-the-art AI to identify the most compelling hooks, transcribe audio with hyper-precision, and automatically render professional 9:16 Shorts with dynamic, customizable subtitles.

## ✨ Features
* **AI-Driven Hook Detection**: Uses OpenAI `gpt-4o-mini` to analyze semantics and select the absolute best story-driven hooks instead of relying on basic heuristics.
* **Whisper Transcription**: High-precision, word-level audio transcription to ensure perfect subtitle pacing.
* **Auto-Cropping & Face Tracking**: Intelligently crops 16:9 video into 9:16 format.
* **Custom Subtitles**: Beautiful ASS (Advanced SubStation) embedded captions with customizable styles (Font, Color, Position).
* **Viral Metadata Generation**: Automatically generates click-worthy titles, descriptions, and hashtags tailored for the algorithm.
* **Raw Downloads**: Easily download the original YouTube Short directly without running the AI pipeline.
* **Local Processing**: Ensures maximum privacy and no recurring API bills for video rendering.

## 🛠 Tech Stack
* **Frontend**: React, Vite, Vanilla CSS
* **Backend**: Python, FastAPI, yt-dlp, ffmpeg-python
* **AI Engine**: OpenAI API, native Whisper-base

## 🚀 Getting Started

### Prerequisites
Make sure you have **FFmpeg**, **Node.js**, and **Python 3.10+** installed on your system.
You will also need an OpenAI API Key.

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ChrisD1231/crispyclips.git
   cd crispyclips
   ```
2. **Setup Backend Environment**:
   Add a `.env` file in the `backend/` directory with your OpenAI API Key:
   `OPENAI_API_KEY=sk-...`

3. **Install Dependencies & Start**:
   You can automatically boot both the frontend and backend using the provided Windows script:
   ```powershell
   .\start.ps1
   ```

## 🎥 The Dashboard
Once started, simply visit `http://localhost:5173`, paste a YouTube Link, and watch CrispyClips automatically generate your social media content!
