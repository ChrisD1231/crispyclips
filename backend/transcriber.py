import whisper
import warnings
import os

warnings.filterwarnings("ignore", message=".*FP16 is not supported.*")

model = None

def get_model():
    global model
    if model is None:
        print("Loading Whisper 'base' model...")
        model = whisper.load_model("base")
    return model

def transcribe_audio(file_path: str):
    """
    Transcribes the given audio/video file and returns segmentation data.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Video file {file_path} not found.")
        
    print(f"Starting transcription for: {file_path}")
    m = get_model()
    # word_timestamps=True required for precise subtitles
    result = m.transcribe(file_path, word_timestamps=True)
    return result
