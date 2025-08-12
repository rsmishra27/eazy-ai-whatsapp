# app/api/whatsapp.py
from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from app.core import graph, config

router = APIRouter()

@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    Body: str = Form(None),
    From: str = Form(...),
    NumMedia: str = Form("0"),
    MediaUrl0: str = Form(None),
):
    """
    Twilio webhook endpoint for WhatsApp sandbox.
    - Twilio sends application/x-www-form-urlencoded with Body, From, NumMedia, MediaUrl0...
    """

    print(f"[webhook] from={From} num_media={NumMedia} body={Body}")

    # send the payload to processing pipeline (agentic graph)
    reply_text = await graph.process_message(
        from_number=From,
        body=Body,
        media_url=MediaUrl0 if NumMedia != "0" else None,
    )

    # Build TwiML response
    resp = MessagingResponse()
    resp.message(reply_text)

    # Twilio expects application/xml
    return Response(content=str(resp), media_type="application/xml")
