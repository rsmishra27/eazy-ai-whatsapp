from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from app.core.prompts import INTENT_PROMPT
from app.core.config import settings

# Global variable for lazy loading
_llm_model = None

def get_llm_model():
    """Lazy load the LLM model to avoid blocking startup."""
    global _llm_model
    if _llm_model is None:
        print("🔄 Loading Gemini LLM model for intent detection...")
        _llm_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        print("✅ Gemini LLM model for intent detection loaded successfully!")
    return _llm_model

def detect_intent_llm(text: str, language: str) -> str:
    if not text:
        return "smalltalk"
    prompt_text = INTENT_PROMPT.format(text=text, language=language)
    try:
        llm_model = get_llm_model()
        human_message = HumanMessage(content=prompt_text)
        response = llm_model.invoke([human_message])
        intent = response.content.strip().lower()
        for valid_intent in ["greet", "product_recommend", "smalltalk"]:
            if valid_intent in intent:
                return valid_intent
        return "product_recommend"
    except Exception as e:
        print(f"[detect_intent_llm] Gemini error: {e}")
        return "product_recommend"