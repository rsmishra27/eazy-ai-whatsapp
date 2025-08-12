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

def generate_reply(prompt: str, user_id: str = None) -> str:
    if not genai_available or not config.GEMINI_API_KEY:
        return f"(demo) I understood: {prompt[:120]}"

    try:
        # Use correct Gemini model name (adjust if your account supports newer versions)
        model = genai.GenerativeModel("models/gemini-1.5-flash")
        response = model.generate_content(prompt)

        # Handle different response formats
        if hasattr(response, "text"):
            return response.text
        elif hasattr(response, "candidates"):
            return response.candidates[0].content.parts[0].text
        else:
            return str(response)
    except Exception as e:
        print("[llm_agent] Gemini call failed:", e)
        return "(LLM error) Sorry, I could not generate a response right now."
