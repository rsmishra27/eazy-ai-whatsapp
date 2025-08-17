#agents/llm_agent.py
from app.core import config

try:
    import google.generativeai as genai
    genai_available = True
except Exception:
    genai_available = False

if genai_available and config.GEMINI_API_KEY:
    genai.configure(api_key=config.GEMINI_API_KEY)

# -------- core reply --------
def generate_reply(prompt: str, language: str = "en") -> str:
    if not genai_available or not config.GEMINI_API_KEY:
        return f"(demo) {prompt[:180]}"
    try:
        # steer response language
        sys_msg = f"You are a concise WhatsApp shopping assistant. Reply in {language}."
        model = genai.GenerativeModel("gemini-2.5-flash")
        resp = model.generate_content([sys_msg, prompt])
        return resp.text.strip()
    except Exception as e:
        print("[llm_agent] Gemini failed:", e)
        return "عذرًا، لا أستطيع الرد الآن." if language == "ar" else "Sorry, I can’t reply right now."

# -------- translation helper (EN↔AR minimal) --------
def translate(text: str, target_lang: str = "ar") -> str:
    if not text:
        return text
    if not genai_available or not config.GEMINI_API_KEY:
        return text  # no-op offline
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"Translate this to {target_lang}. Only output the translation.\n\n{text}"
        resp = model.generate_content(prompt)
        return resp.text.strip()
    except Exception as e:
        print("[llm_agent] translate failed:", e)
        return text
