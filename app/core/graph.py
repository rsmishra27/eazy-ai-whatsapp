# app/core/graph.py
import asyncio
from typing import Optional
from app.agents import llm_agent, stt_tool
from app.core import storage, config

async def process_message(from_number: str, body: Optional[str], media_url: Optional[str]) -> str:
    """
    Simple agentic pipeline:
    - If media_url present: transcribe (STT) -> store -> pass transcript to LLM
    - Else: pass text body to LLM
    """
    # If audio present → transcribe
    text_input = body
    if media_url:
        # stt_tool.transcribe_audio is synchronous; run in threadpool to avoid blocking
        loop = asyncio.get_running_loop()
        transcript = await loop.run_in_executor(None, stt_tool.transcribe_audio, media_url)
        # store transcription
        storage.store_transcript(from_number, transcript)
        text_input = transcript

    # simple guard: if no text at all
    if not text_input or text_input.strip() == "":
        return "Sorry, I couldn't read that. Can you please send a text or voice message again?"

    # prepare a prompt for LLM — you can make this richer with context/history
    prompt = f"User ({from_number}) said: {text_input}\nRespond concisely as a friendly shopping assistant with short suggestions."

    # call the LLM agent
    reply = llm_agent.generate_reply(prompt=prompt, user_id=from_number)
    return reply
