import os

def generate_ass_subtitle(segment, output_path: str, video_width: int, video_height: int, font: str = "Arial Black", color: str = "&H00FFFFFF", highlight: str = "&H0000FFFF", position: str = "Middle"):
    """
    Generates an Advanced SubStation Alpha (.ass) file optimized for TikTok/Shorts style.
    """
    # Map Position strings to ASS margins
    margin_v = 350
    if position == "Top": margin_v = 700
    if position == "Bottom": margin_v = 150
    
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_width}
PlayResY: {video_height}
WrapStyle: 1

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font},48,{color},&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,0,2,10,10,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    def format_time(seconds):
        if seconds < 0: seconds = 0
        h = int(seconds / 3600)
        m = int((seconds % 3600) / 60)
        s = int(seconds % 60)
        cs = int((seconds * 100) % 100)
        return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

    events = []
    clip_start = segment['start']
    words_data = segment.get('words', [])
    
    if words_data:
        chunks = []
        current_chunk = []
        MAX_WORDS = 3
        
        for w in words_data:
            current_chunk.append(w)
            if len(current_chunk) >= MAX_WORDS:
                chunks.append(current_chunk)
                current_chunk = []
        if current_chunk:
            chunks.append(current_chunk)
            
        for chunk in chunks:
            chunk_start = chunk[0]['start'] - clip_start
            chunk_end = chunk[-1]['end'] - clip_start
            
            styled_words = []
            for i, w_data in enumerate(chunk):
                word = w_data['word'].strip().upper()
                if i % 3 == 0 or len(word) > 5:
                    # Highlight color dynamically requested
                    styled_words.append(f"{{\\c{highlight}}}{word}{{\\c{color}}}")
                else:
                    styled_words.append(word)
            
            text_line = " ".join(styled_words)
            events.append(f"Dialogue: 0,{format_time(chunk_start)},{format_time(chunk_end)},Default,,0,0,0,,{text_line}\n")
    else:
        # Fallback if words aren't available
        start_time = format_time(0)
        duration = segment['end'] - segment['start']
        end_time = format_time(duration)
        text = segment['text'].strip()
        events.append(f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{text}\n")
        
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header + "".join(events))
        
    return output_path
