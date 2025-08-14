# app/agents/stt_tool.py
import requests
import time
from requests.auth import HTTPBasicAuth
from app.core import config

ASSEMBLY_HEADERS = {
    "authorization": config.ASSEMBLYAI_API_KEY
} if config.ASSEMBLYAI_API_KEY else {}

def transcribe_audio(audio_url: str) -> str:
    """
    Downloads audio from Twilio media URL, uploads to AssemblyAI, 
    and polls for a transcript.
    """
    if not config.ASSEMBLYAI_API_KEY:
        return "(stt disabled) Transcription not available - no AssemblyAI API key."

    # 1) Download the audio from Twilio media URL with authentication
    try:
        res = requests.get(
            audio_url,
            auth=HTTPBasicAuth(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
        )
    except Exception as e:
        return f"(stt error) failed to download audio: {e}"

    if res.status_code != 200:
        return f"(stt error) could not download audio: {res.status_code}"

    # 2) Upload to AssemblyAI
    try:
        upload_resp = requests.post(
            "https://api.assemblyai.com/v2/upload",
            headers=ASSEMBLY_HEADERS,
            data=res.content
        )
        upload_resp.raise_for_status()
        upload_url = upload_resp.json().get("upload_url")
    except Exception as e:
        return f"(stt error) failed to upload to AssemblyAI: {e}"

    # 3) Request transcript
    try:
        transcript_req = {"audio_url": upload_url}
        tr_res = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            json=transcript_req,
            headers=ASSEMBLY_HEADERS
        )
        tr_res.raise_for_status()
        transcript_id = tr_res.json()["id"]
    except Exception as e:
        return f"(stt error) failed to request transcript: {e}"

    # 4) Poll until done
    poll_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    for _ in range(60):  # up to ~90 seconds
        time.sleep(1.5)
        status = requests.get(poll_url, headers=ASSEMBLY_HEADERS).json()
        if status.get("status") == "completed":
            transcript_text = status.get("text", "")
            print(f"[stt_tool] Transcript: {transcript_text}")  # ✅ Console log
            return transcript_text
        if status.get("status") == "error":
            return f"(stt error) {status.get('error')}"

    return "(stt timeout) transcription not ready yet"
