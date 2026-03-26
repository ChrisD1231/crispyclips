import ffmpeg
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from face_tracker import get_center_crop_coordinates

load_dotenv()
try:
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except BaseException:
    # If API key is still missing or invalid, bypass the hard crash so fallback works.
    client = OpenAI(api_key="sk-fallback_dummy_key_to_prevent_crash")
    client.api_key = None # Manually clear it to trigger fallback


def fallback_extract_engaging_segments(transcript_data, min_duration=15, max_duration=60):
    segments = transcript_data.get("segments", [])
    if not segments:
        return []

    clips = []
    current_clip = None
    
    for seg in segments:
        start = seg['start']
        end = seg['end']
        text = seg['text'].strip()
        words = seg.get('words', [])
        
        if current_clip is None:
            current_clip = {
                "start": start,
                "end": end,
                "text": text,
                "words": words,
                "word_count": len(text.split())
            }
        else:
            duration = end - current_clip['start']
            
            is_sentence_end = text.endswith(('.', '?', '!', '...'))
            if (duration >= 30 and is_sentence_end) or duration > max_duration:
                final_dur = current_clip['end'] - current_clip['start']
                score = current_clip['word_count'] / final_dur if final_dur > 0 else 0
                current_clip['score'] = int(score * 100)
                
                if final_dur >= min_duration:
                    current_clip['title'] = current_clip['text'][:30] + "..."
                    clips.append(current_clip)
                
                current_clip = {
                    "start": start,
                    "end": end,
                    "text": text,
                    "words": words,
                    "word_count": len(text.split())
                }
            else:
                current_clip['end'] = end
                current_clip['text'] += " " + text
                current_clip['words'].extend(words)
                current_clip['word_count'] += len(text.split())
                
    if current_clip:
        final_dur = current_clip['end'] - current_clip['start']
        if final_dur >= min_duration:
            score = current_clip['word_count'] / final_dur if final_dur > 0 else 0
            current_clip['score'] = int(score * 100)
            current_clip['title'] = current_clip['text'][:30] + "..."
            clips.append(current_clip)
            
    clips.sort(key=lambda x: x['score'], reverse=True)
    return clips[:5]

def extract_engaging_segments(transcript_data, min_duration=15, max_duration=60):
    """
    Analyzes the whisper transcript to find engaging segments via OpenAI GPT-4o-mini.
    Returns a list of dictionaries with 'start', 'end', 'score', 'words', 'text', 'title'.
    """
    segments = transcript_data.get("segments", [])
    if not segments:
        return []

    if not client.api_key:
        print("No OpenAI API Key found, using fallback clipping.")
        return fallback_extract_engaging_segments(transcript_data, min_duration, max_duration)

    # 1. Build a timeline string for the prompt
    timeline = ""
    for seg in segments:
        start = round(seg['start'], 1)
        end = round(seg['end'], 1)
        text = seg['text'].strip()
        timeline += f"[{start}s - {end}s] {text}\n"

    # 2. Query OpenAI
    system_prompt = f"""
You are an expert video editor. I will give you a transcript of a video with timestamps.
Find the top 5 most engaging, viral, and standalone segments. 
Each segment MUST be between {min_duration} and {max_duration} seconds long. 
Let the start and end times correspond EXACTLY to natural conversational breaks based on the provided timestamps.
Return your answer exactly as a JSON object with a "clips" array.
Each object in the array must have:
- "start_time": (float) the start timestamp (e.g. 15.2)
- "end_time": (float) the end timestamp (e.g. 50.5)
- "title": (string) a short 30-char max title
- "score": (int) a virality score from 1-100

Example format:
{{
  "clips": [
    {{"start_time": 12.5, "end_time": 45.2, "title": "The Big Reveal", "score": 95}}
  ]
}}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": timeline}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        content = response.choices[0].message.content
        ai_data = json.loads(content)
        ai_clips = ai_data.get("clips", [])
    except Exception as e:
        print(f"OpenAI error during clipping, falling back: {e}")
        return fallback_extract_engaging_segments(transcript_data, min_duration, max_duration)

    # 3. Reconstruct full clip data mapping back to exact word timestamps
    flat_words = []
    for seg in segments:
        flat_words.extend(seg.get('words', []))
        
    final_clips = []
    
    for clip in ai_clips:
        c_start = float(clip.get("start_time", 0))
        c_end = float(clip.get("end_time", 0))
        
        # Find all words within this chunk (with a small 1s buffer for alignment safety)
        clip_words = []
        for w in flat_words:
            w_start = w.get('start', 0)
            w_end = w.get('end', 0)
            if w_end > c_start - 0.5 and w_start < c_end + 0.5:
                clip_words.append(w)
                
        if not clip_words:
            continue
            
        exact_start = clip_words[0]['start']
        exact_end = clip_words[-1]['end']
        
        # Whisper words dicts usually have a 'word' key, e.g., {'word': ' Hello', 'start': 0.0, 'end': 0.5}
        clip_text = "".join([w.get('word', '') for w in clip_words]).strip()
        
        final_clips.append({
            "start": exact_start,
            "end": exact_end,
            "text": clip_text,
            "words": clip_words,
            "word_count": len(clip_words),
            "score": int(clip.get("score", 80)),
            "title": str(clip.get("title", clip_text[:30] + "..."))
        })

    # Sort final clips by score
    final_clips.sort(key=lambda x: x['score'], reverse=True)
    
    # If LLM failed to give clips, fallback
    if not final_clips:
        return fallback_extract_engaging_segments(transcript_data, min_duration, max_duration)
        
    return final_clips[:5]

def render_clip(video_path: str, start: float, end: float, output_path: str, subtitle_path: str = None):
    """
    Renders the highlighted segment, cropping it to 9:16.
    """
    x, y, w, h = get_center_crop_coordinates(video_path)
    
    try:
        stream = ffmpeg.input(video_path, ss=start, to=end)
        video = stream.video.crop(x, y, w, h)
        
        if subtitle_path:
            # ffmpeg windows subtitle escaping using relative forward slashes
            sub_escaped = subtitle_path.replace("\\", "/")
            video = video.filter('ass', sub_escaped)
            
        audio = stream.audio
        
        out = ffmpeg.output(video, audio, output_path, vcodec='libx264', acodec='aac', preset='veryfast', strict='experimental', loglevel="error")
        ffmpeg.run(out, capture_stderr=True, overwrite_output=True)
        return output_path
    except ffmpeg.Error as e:
        error_msg = e.stderr.decode('utf8') if e.stderr else "Unknown FFMPEG Error"
        print(f"FFMPEG Error: {error_msg}")
        raise RuntimeError(f"FFMPEG failed to render video: {error_msg}")
