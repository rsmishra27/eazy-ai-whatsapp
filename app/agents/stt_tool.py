import assemblyai as aai
from app.core.config import settings
import requests

aai.settings.api_key = settings.ASSEMBLYAI_API_KEY

def transcribe_audio_from_url(audio_url: str) -> str:
    """
    Transcribes an audio file from a URL using AssemblyAI.
    
    Args:
        audio_url: The public URL of the audio file.
    
    Returns:
        The transcribed text string or None if transcription fails.
    """
    try:
        # AssemblyAI API requires a public URL
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(audio_url)
        
        if transcript.status == aai.TranscriptStatus.error:
            print(f"AssemblyAI transcription failed: {transcript.error}")
            return None
        
        return transcript.text
    except Exception as e:
        print(f"Error during AssemblyAI transcription: {e}")
        return None