# app/api/whatsapp.py
from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from app.core import graph, config
from app.agents.stt_tool import transcribe_audio

router = APIRouter()

@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    Body: str = Form(None),
    From: str = Form(...),
    NumMedia: str = Form("0"),
    MediaUrl0: str = Form(None),
    MediaContentType0: str = Form(None)
):
    """
    Handles both text and voice messages from WhatsApp via Twilio.
    """

    print(f"[webhook] from={From} num_media={NumMedia} body={Body}")

    message_text = Body

    # Detect if incoming media is audio (voice note)
    if NumMedia != "0" and MediaContentType0 and "audio" in MediaContentType0:
        print(f"[webhook] Received voice note: {MediaUrl0}")
        message_text = transcribe_audio(MediaUrl0)
        print(f"[webhook] Transcribed text: {message_text}")

    # Pass text (from user or STT) to the LLM processing pipeline
    reply_text = await graph.process_message(
        from_number=From,
        body=message_text,
        media_url=None
    )

    # Build TwiML response
    resp = MessagingResponse()
    resp.message(reply_text)

    return Response(content=str(resp), media_type="application/xml")
