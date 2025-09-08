# app/agents/stt_tools.py
import os
import tempfile
import requests
import assemblyai as aai
from typing import Optional
from app.core.config import settings

aai.settings.api_key = settings.ASSEMBLYAI_API_KEY

def transcribe_audio_from_url(audio_url: str) -> Optional[str]:
    """Download WhatsApp voice note from Twilio and transcribe with AssemblyAI."""
    if not audio_url:
        return None

    auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    local_path = None

    try:
        # 1. Download from Twilio with auth
        r = requests.get(audio_url, auth=auth, stream=True, timeout=30)
        r.raise_for_status()

        suffix = ".ogg"  # WhatsApp voice notes are usually ogg/opus
        fd, local_path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

        # 2. Transcribe locally
        transcriber = aai.Transcriber()
        config = aai.TranscriptionConfig(
            language_detection=True,  # auto-detect English/Arabic
            punctuate=True,
            format_text=True
        )
        transcript = transcriber.transcribe(local_path, config=config)

        if transcript.status == aai.TranscriptStatus.error:
            print(f"[STT] AssemblyAI error: {transcript.error}")
            return None

        return transcript.text

    except Exception as e:
        print(f"[STT] Error: {e}")
        return None

    finally:
        if local_path and os.path.exists(local_path):
            os.remove(local_path)