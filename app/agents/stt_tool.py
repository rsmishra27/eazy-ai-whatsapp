# app/agents/stt_tool.py
import requests
import time
from app.core import config

ASSEMBLY_HEADERS = {
    "authorization": config.ASSEMBLYAI_API_KEY
} if config.ASSEMBLYAI_API_KEY else {}

def transcribe_audio(audio_url: str):
    """
    Uploads audio (by URL) to AssemblyAI and polls for a transcript + detected language.
    Returns: (transcript_text, language_code)
    """
    if not config.ASSEMBLYAI_API_KEY:
        return "(stt disabled) No AssemblyAI API key.", "unknown"

    # 1) Download audio from Twilio with auth
    res = requests.get(audio_url, auth=(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN))
    if res.status_code != 200:
        return f"(stt error) could not download audio: {res.status_code}", "unknown"

    # 2) Upload to AssemblyAI
    upload_resp = requests.post(
        "https://api.assemblyai.com/v2/upload",
        headers=ASSEMBLY_HEADERS,
        data=res.content
    )
    upload_resp.raise_for_status()
    upload_url = upload_resp.json().get("upload_url")

    # 3) Request transcript with auto language detection
    transcript_req = {
        "audio_url": upload_url,
        "language_detection": True
    }
    tr_res = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        json=transcript_req,
        headers=ASSEMBLY_HEADERS
    )
    tr_res.raise_for_status()
    transcript_id = tr_res.json()["id"]

    # 4) Poll until complete
    poll_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    for _ in range(60):
        time.sleep(1.5)
        status = requests.get(poll_url, headers=ASSEMBLY_HEADERS).json()
        if status.get("status") == "completed":
            transcript_text = status.get("text", "")
            lang_code = status.get("language_code", "unknown")
            print(f"[stt_tool] Transcript: {transcript_text}")
            print(f"[stt_tool] Language: {lang_code}")
            return transcript_text, lang_code
        if status.get("status") == "error":
            return f"(stt error) {status.get('error')}", "unknown"

    return "(stt timeout) transcription not ready yet", "unknown"
