from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage
from app.core.prompts import INTENT_PROMPT

llm_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

def detect_intent_llm(text: str, language: str) -> str:
    if not text:
        return "smalltalk"
    prompt_text = INTENT_PROMPT.format(text=text, language=language)
    try:
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
