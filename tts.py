# backend/tts.py
import uuid
from pathlib import Path
import pyttsx3

TTS_DIR = Path(__file__).parent / "uploads" / "tts"
TTS_DIR.mkdir(parents=True, exist_ok=True)

def synthesize_text_to_file(text: str):
    filename = f"tts_{uuid.uuid4().hex}.wav"
    outpath = TTS_DIR / filename

    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    engine.save_to_file(text, str(outpath))
    engine.runAndWait()
    return str(outpath)
