import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def generate_youtube_metadata(transcript: str):
    """
    Generates a viral title, description, and tags for a YouTube Short based on the transcript.
    Returns a dict with 'title', 'description', and 'tags'.
    """
    if not client.api_key:
        # Fallback if no key is present
        return {
            "title": transcript[:30] + "...",
            "description": "Auto-generated short.\n\nTranscript:\n" + transcript,
            "tags": ["shorts", "viral"]
        }

    prompt = f"""
    You are a professional YouTube Shorts and TikTok editor who makes highly viral content for million-subscriber channels.
    I will provide you with a raw transcript of a clip you just cut.
    
    Please generate:
    1. A hyper-engaging VISUAL Hook Title (under 60 characters) that creates a MASSIVE curiosity gap. Avoid cringe phrases. It should sound legit. Do not put quotes around it. Do not use hashtags in the title.
    2. A punchy 1-2 sentence Description that sells the clip, followed by EXACTLY 3 highly relevant hashtags.
    3. A comma-separated list of 5 broad, SEO-friendly tags.

    Return EXACTLY in this strict format:
    TITLE: <title here>
    DESCRIPTION: <description here>
    TAGS: <tag1, tag2, tag3>

    Transcript:
    "{transcript}"
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        
        content = response.choices[0].message.content.strip()
        
        # Parse output
        title = "Viral Short"
        description = ""
        tags = ["shorts"]
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('TITLE:'):
                title = line.replace('TITLE:', '').strip()
            elif line.startswith('DESCRIPTION:'):
                description = line.replace('DESCRIPTION:', '').strip()
            elif line.startswith('TAGS:'):
                tags = [t.strip() for t in line.replace('TAGS:', '').split(',')]
                
        return {
            "title": title,
            "description": description,
            "tags": tags
        }
    except Exception as e:
        print(f"OpenAI Generation Error: {e}")
        return {
            "title": transcript[:30] + "...",
            "description": transcript,
            "tags": ["shorts"]
        }
