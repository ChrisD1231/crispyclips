import yt_dlp
import os

def download_video(url: str, output_dir: str = "downloads"):
    """
    Downloads the best quality video and audio from YouTube.
    Returns the paths to the video file and its corresponding ID.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    ydl_opts = {
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'quiet': False,
        'noplaylist': True
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        video_id = info_dict.get("id")
        title = info_dict.get("title", "Untitled")
        downloaded_file = os.path.join(output_dir, f"{video_id}.mp4")
        return downloaded_file, title, video_id
