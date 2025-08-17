from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
import re

llm_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

def detect_language(text: str) -> str:
    """
    Detects the language of the text using the LLM.
    Returns 'ar' for Arabic, 'en' for English, or 'en' as default.
    """
    if not text:
        return "en"
    
    try:
        prompt = f"Detect the language of the following text: '{text}'. Reply with only 'en' for English or 'ar' for Arabic."
        human_message = HumanMessage(content=prompt)
        response = llm_model.invoke([human_message])
        
        detected_lang = response.content.strip().lower()
        if "ar" in detected_lang:
            return "ar"
        return "en"
        
    except Exception as e:
        print(f"[detect_language] LLM error: {e}")
        return "en"