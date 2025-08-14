# app/api/whatsapp.py
from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from langdetect import detect
from app.core import graph
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
    print(f"[webhook] from={From} num_media={NumMedia} body={Body}")

    reply_text = None
    lang_code = "en"  # Default to English if detection fails

    if NumMedia != "0" and MediaUrl0:
        transcript, lang_code = transcribe_audio(MediaUrl0)
        print(f"[webhook] Transcribed text: {transcript}")
        print(f"[webhook] Detected language: {lang_code}")

        reply_text = await graph.process_message(
            from_number=From,
            body=transcript,
            media_url=MediaUrl0,
            language=lang_code
        )
    else:
        # Plain text message
        if Body:
            try:
                lang_code = detect(Body)
                print(f"[webhook] Detected text language: {lang_code}")
            except Exception as e:
                print("[webhook] Language detection failed:", e)
            reply_text = await graph.process_message(
                from_number=From,
                body=Body,
                media_url=None,
                language=lang_code
            )

    if not reply_text:
        reply_text = "⚠️ Sorry, I couldn't process that."

    resp = MessagingResponse()
    resp.message(reply_text)

    return Response(content=str(resp), media_type="application/xml")
