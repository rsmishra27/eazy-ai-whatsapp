# app/agents/stt_tool.py
import requests
import time
from app.core import config

ASSEMBLY_HEADERS = {"authorization": config.ASSEMBLYAI_API_KEY} if config.ASSEMBLYAI_API_KEY else {}

def transcribe_audio(audio_url: str) -> str:
    """
    Uploads audio (by URL) to AssemblyAI and polls for a transcript.
    NOTE: This is a simple synchronous function intended for demo/testing.
    Replace/adjust per AssemblyAI API version.
    """
    if not config.ASSEMBLYAI_API_KEY:
        return "(stt disabled) Transcription not available - no AssemblyAI API key."

    # 1) Download the audio from Twilio media URL
    res = requests.get(audio_url)
    if res.status_code != 200:
        return f"(stt error) could not download audio: {res.status_code}"

    # 2) Upload to AssemblyAI
    upload_resp = requests.post(
        "https://api.assemblyai.com/v2/upload",
        headers=ASSEMBLY_HEADERS,
        data=res.content
    )
    upload_resp.raise_for_status()
    upload_url = upload_resp.json().get("upload_url")

    # 3) Request transcript
    transcript_req = {"audio_url": upload_url}
    tr_res = requests.post("https://api.assemblyai.com/v2/transcript", json=transcript_req, headers=ASSEMBLY_HEADERS)
    tr_res.raise_for_status()
    transcript_id = tr_res.json()["id"]

    # 4) Poll until done
    poll_url = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"
    for _ in range(60):  # up to ~60 checks
        time.sleep(1.5)
        status = requests.get(poll_url, headers=ASSEMBLY_HEADERS).json()
        if status.get("status") == "completed":
            return status.get("text", "")
        if status.get("status") == "error":
            return f"(stt error) {status.get('error')}"
    return "(stt timeout) transcription not ready yet"
