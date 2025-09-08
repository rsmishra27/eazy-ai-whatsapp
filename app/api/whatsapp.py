# app/api/whatsapp.py
import os
from fastapi import APIRouter, Form, Request, HTTPException
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from app.core.config import settings
from app.core.langgraph_app import run_message
from app.agents.stt_tool import transcribe_audio_from_url  # if your file is stt_tools.py, keep that import

router = APIRouter()
validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)

def get_twilio_xml_response(body: str) -> Response:
    """Return a proper TwiML XML response with correct content-type."""
    if not body or body.isspace():
        body = "Sorry, I can't generate a response right now. Please try again."

    twilio_resp = MessagingResponse()
    twilio_resp.message(body)
    # IMPORTANT: return XML content-type so Twilio parses it
    return Response(content=str(twilio_resp), media_type="application/xml")

@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(None),
    MediaUrl0: str = Form(None)
):
    """
    Handles incoming messages from WhatsApp via Twilio.
    - Transcribes audio messages using AssemblyAI.
    - Passes text to the LangGraph application for processing.
    """

    # Skip Twilio signature validation for testing
    # Uncomment the block below for production use
    """
    twilio_signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    form = dict(await request.form())
    if settings.TWILIO_AUTH_TOKEN:
        if not validator.validate(url, form, twilio_signature):
            # If validation fails, return 403 to avoid spoofed requests
            raise HTTPException(status_code=403, detail="Invalid Twilio signature")
    """

    user_id = From.split("whatsapp:")[-1] if "whatsapp:" in From else From

    try:
        if MediaUrl0:
            print(f"Received audio message from {user_id}")
            text_content = transcribe_audio_from_url(MediaUrl0)
            if not text_content:
                return get_twilio_xml_response("Sorry, I could not transcribe that audio.")
        else:
            print(f"Received text message from {user_id}: {Body}")
            text_content = Body or ""

        llm_response = await run_message(user_id=user_id, text=text_content)
        return get_twilio_xml_response(llm_response)

    except Exception as e:
        print(f"Error processing message: {e}")
        return get_twilio_xml_response("An error occurred. Please try again later.")