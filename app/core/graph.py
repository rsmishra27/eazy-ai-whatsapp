# app/core/graph.py
from app.core.vector_search import search_similar_products
import asyncio
from typing import Optional
from app.agents import stt_tool
from app.core import storage

async def process_message(from_number: str, body: Optional[str], media_url: Optional[str], language: Optional[str] = None) -> str:
    text_input = body
    lang_code = language

    if media_url:
        loop = asyncio.get_running_loop()
        transcript, detected_lang = await loop.run_in_executor(None, stt_tool.transcribe_audio, media_url)
        storage.store_transcript(from_number, transcript)
        text_input = transcript
        lang_code = detected_lang

    if not text_input or text_input.strip() == "":
        return "Sorry, I couldn't read that. Can you please send a text or voice message again?"

    # Use semantic search to recommend products
    recommended = search_similar_products(text_input, top_k=3)

    # Format product recommendations into a reply message
    reply = "Here are some products you might like:\n"
    for p in recommended:
        reply += f"- {p['name']} (${p['price']})\n"

    return reply
