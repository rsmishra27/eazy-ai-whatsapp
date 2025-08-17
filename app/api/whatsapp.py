from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from app.core.langgraph_app import run_message
from app.agents.stt_tool import transcribe_audio

router = APIRouter()

@router.post("/webhook")
async def whatsapp_webhook(
    request: Request,
    Body: str = Form(None),
    From: str = Form(...),
    NumMedia: str = Form("0"),
    MediaUrl0: str = Form(None),
):
    if NumMedia != "0" and MediaUrl0:
        transcript, lang_code = transcribe_audio(MediaUrl0)
        reply_text = run_message(user_id=From, text=transcript, language=lang_code or None)
    else:
        reply_text = run_message(user_id=From, text=Body or "")
    if not reply_text:
        reply_text = "⚠️ Sorry, I couldn't process that."
    resp = MessagingResponse()
    resp.message(reply_text)
    return Response(content=str(resp), media_type="application/xml")
