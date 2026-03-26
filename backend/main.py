import os
import sys
# Inject venv/Scripts into PATH so ffmpeg can be found by yt-dlp, whisper, and ffmpeg-python
os.environ["PATH"] = os.path.abspath(os.path.join("venv", "Scripts")) + os.pathsep + os.environ.get("PATH", "")

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from typing import Dict, Any

from downloader import download_video
from transcriber import transcribe_audio
from clipper import extract_engaging_segments, render_clip
from subtitle_gen import generate_ass_subtitle
from metadata_gen import generate_youtube_metadata

app = FastAPI(title="Crispy Clips API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str
    target_duration_min: int = 15
    target_duration_max: int = 60

# In-memory job store
jobs: Dict[str, Any] = {}

def process_pipeline(job_id: str, url: str, min_d: int, max_d: int):
    try:
        jobs[job_id]["status"] = "Downloading Video from YouTube..."
        jobs[job_id]["progress"] = 10
        video_path, title, vid_id = download_video(url)
        
        jobs[job_id]["status"] = "Transcribing Audio & Detecting Hooks..."
        jobs[job_id]["progress"] = 30
        transcript = transcribe_audio(video_path)
        
        jobs[job_id]["status"] = "Analyzing Segments for Virality..."
        jobs[job_id]["progress"] = 60
        segments = extract_engaging_segments(transcript, min_d, max_d)
        
        jobs[job_id]["video_path"] = video_path
        jobs[job_id]["segments"] = segments
        
        jobs[job_id]["status"] = f"Rendering {len(segments)} clips with Auto-Captions..."
        jobs[job_id]["progress"] = 80
        
        clips_rendered = []
        for i, seg in enumerate(segments):
            clip_name = f"{vid_id}_clip_{i}.mp4"
            clip_path = os.path.join("downloads", clip_name)
            
            sub_name = f"{vid_id}_sub_{i}.ass"
            sub_path = os.path.join("downloads", sub_name)
            
            # Default 1080p target mapping (9:16) ~ 607x1080
            generate_ass_subtitle(seg, sub_path, 607, 1080)
            
            render_clip(video_path, seg['start'], seg['end'], clip_path, sub_path)
            
            # Generate OpenAI Titles & Descriptions
            metadata = generate_youtube_metadata(seg['text'])
            
            clips_rendered.append({
                "url": f"http://localhost:8000/downloads/{clip_name}",
                "title": metadata['title'],
                "description": metadata['description'],
                "tags": metadata['tags'],
                "score": seg['score'],
                "duration": round(seg['end'] - seg['start'], 1)
            })
            
        jobs[job_id]["status"] = "Completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["result"] = clips_rendered
        
    except Exception as e:
        jobs[job_id]["status"] = "Failed"
        jobs[job_id]["error"] = str(e)
        import traceback
        traceback.print_exc()

@app.post("/api/process")
async def start_processing(request: VideoRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "id": job_id,
        "status": "Starting up...",
        "progress": 0,
        "result": None,
        "error": None
    }
    background_tasks.add_task(process_pipeline, job_id, request.url, request.target_duration_min, request.target_duration_max)
    return {"job_id": job_id}

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

class RawRequest(BaseModel):
    url: str

@app.post("/api/download_raw")
async def download_raw_endpoint(req: RawRequest):
    try:
        video_path, title, vid_id = download_video(req.url)
        clip_name = os.path.basename(video_path)
        return {
            "success": True,
            "url": f"http://localhost:8000/downloads/{clip_name}",
            "title": title
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RerenderRequest(BaseModel):
    job_id: str
    clip_index: int
    font: str
    color: str
    position: str

@app.post("/api/rerender")
async def rerender_clip(req: RerenderRequest):
    if req.job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
        
    job = jobs[req.job_id]
    video_path = job.get("video_path")
    segments = job.get("segments")
    
    if not video_path or not segments or req.clip_index >= len(segments):
        raise HTTPException(status_code=400, detail="Invalid job data or clip index")
        
    seg = segments[req.clip_index]
    vid_id = os.path.basename(video_path).split('.')[0]
    
    clip_name = f"{vid_id}_clip_{req.clip_index}.mp4"
    clip_path = os.path.join("downloads", clip_name)
    sub_name = f"{vid_id}_sub_{req.clip_index}.ass"
    sub_path = os.path.join("downloads", sub_name)
    
    generate_ass_subtitle(seg, sub_path, 607, 1080, font=req.font, color=req.color, highlight="&H0000FFFF", position=req.position)
    
    render_clip(video_path, seg['start'], seg['end'], clip_path, sub_path)
    
    import time
    new_url = f"http://localhost:8000/downloads/{clip_name}?t={int(time.time())}"
    
    if job.get("result"):
        job["result"][req.clip_index]["url"] = new_url
        
    return {"success": True, "url": new_url}

from fastapi.staticfiles import StaticFiles
os.makedirs("downloads", exist_ok=True)
app.mount("/downloads", StaticFiles(directory="downloads"), name="downloads")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
