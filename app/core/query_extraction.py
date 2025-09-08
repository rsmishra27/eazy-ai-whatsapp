from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from app.core.prompts import QUERY_EXTRACTION_PROMPT

# Global variable for lazy loading
_llm_model = None

def get_llm_model():
    """Lazy load the LLM model to avoid blocking startup."""
    global _llm_model
    if _llm_model is None:
        print("🔄 Loading Gemini LLM model for query extraction...")
        _llm_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        print("✅ Gemini LLM model for query extraction loaded successfully!")
    return _llm_model

def extract_query(text: str, language: str) -> str:
    """
    Extracts a concise search query from a conversational text using the LLM.
    """
    prompt = QUERY_EXTRACTION_PROMPT.format(text=text, language=language)
    try:
        llm_model = get_llm_model()
        human_message = HumanMessage(content=prompt)
        response = llm_model.invoke([human_message])
        return response.content.strip()
    except Exception as e:
        print(f"[extract_query] Gemini error: {e}")
        return text