from fastapi import APIRouter, Form
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from app.core.config import settings
from app.core.langgraph_app import run_message
from app.agents.stt_tool import transcribe_audio_from_url
import os

router = APIRouter()
validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)

def get_response(body: str):
    """Generates a Twilio MessagingResponse object with the given body."""
    response = MessagingResponse()
    response.message(body)
    return str(response)

@router.post("/")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(None),
    MediaUrl0: str = Form(None)
):
    """
    Handles incoming messages from WhatsApp via Twilio.
    - Transcribes audio messages using AssemblyAI.
    - Passes text to the LangGraph application for processing.
    """
    user_id = From.split("whatsapp:")[1]

    try:
        if MediaUrl0:
            # Handle audio message
            print(f"Received audio message from {user_id}")
            text_content = transcribe_audio_from_url(MediaUrl0)
            if not text_content:
                return get_response("Sorry, I could not transcribe that audio.")
        else:
            # Handle text message
            print(f"Received text message from {user_id}: {Body}")
            text_content = Body

        # Run the LangGraph agent to get a response
        llm_response = await run_message(user_id=user_id, text=text_content)
        
        return get_response(llm_response)

    except Exception as e:
        print(f"Error processing message: {e}")
        return get_response("An error occurred. Please try again later.")