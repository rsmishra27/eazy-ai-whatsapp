# app/agents/llm_agent.py
import os
from app.core import config

try:
    import google.generativeai as genai
    genai_available = True
except Exception:
    genai_available = False

if genai_available and config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)

def generate_reply(prompt: str, user_id: str = None, language: str = None) -> str:
    """
    Generate a reply for the given prompt.
    If language is provided, instruct Gemini to reply in that language.
    """
    if not genai_available or not config.GEMINI_API_KEY:
        return f"(demo) I understood: {prompt[:120]}"

    try:
        # Add language instruction if given
        if language and language not in ["en", "eng", "en-US"]:
            prompt = f"Reply in {language}. User said: {prompt}"

        model = genai.GenerativeModel("gemini-2.5-flash")


        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("[llm_agent] Gemini call failed:", e)
        return f"(LLM error) Sorry, I could not generate a response right now."
# app/api/whatsapp.py
from fastapi import APIRouter, Form, Request
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from app.core import graph, config
from app.agents.stt_tool import transcribe_audio  # For voice transcription

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
    Twilio webhook endpoint for WhatsApp.
    Handles both text and voice messages.
    """

    print(f"[webhook] from={From} num_media={NumMedia} body={Body}")

    reply_text = None

    if NumMedia != "0" and MediaUrl0:  
        # Voice message handling
        print(f"[webhook] Received voice note: {MediaUrl0}")

        transcript, lang_code = transcribe_audio(MediaUrl0)  
        print(f"[webhook] Transcribed text: {transcript}")
        print(f"[webhook] Detected language: {lang_code}")

        # Pass transcript + language to processing pipeline
        reply_text = await graph.process_message(
            from_number=From,
            body=transcript,
            language=lang_code
        )
    else:
        # Normal text message
        reply_text = await graph.process_message(
            from_number=From,
            body=Body
        )

    # Build TwiML response
    resp = MessagingResponse()
    resp.message(reply_text)

    return Response(content=str(resp), media_type="application/xml")
