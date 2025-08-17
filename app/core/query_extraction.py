from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from app.core.prompts import QUERY_EXTRACTION_PROMPT

llm_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

def extract_query(text: str, language: str) -> str:
    """
    Extracts a concise search query from a conversational text using the LLM.
    """
    prompt = QUERY_EXTRACTION_PROMPT.format(text=text, language=language)
    try:
        human_message = HumanMessage(content=prompt)
        response = llm_model.invoke([human_message])
        return response.content.strip()
    except Exception as e:
        print(f"[extract_query] Gemini error: {e}")
        return text