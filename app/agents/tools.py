from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.vector_search import search_similar_products
from app.core.prompts import CHAT_GREET_PROMPT, PRODUCT_RECOMMEND_PROMPT
from langchain.schema import HumanMessage, AIMessage

# Global variable for lazy loading
_chat_llm = None

def get_chat_llm():
    """Lazy load the chat LLM model to avoid blocking startup."""
    global _chat_llm
    if _chat_llm is None:
        print("🔄 Loading Gemini LLM model for chat tools...")
        _chat_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        print("✅ Gemini LLM model for chat tools loaded successfully!")
    return _chat_llm

def product_recommend(query: str, language: str = "en") -> AIMessage:
    """
    Searches for and formats a response with the top 3 product recommendations.
    """
    results = search_similar_products(query, top_k=3)
    
    prompt_text = PRODUCT_RECOMMEND_PROMPT.format(
        text=query,
        language=language,
        products=results
    )
    
    try:
        chat_llm = get_chat_llm()
        human_message = HumanMessage(content=prompt_text)
        response = chat_llm.invoke([human_message])
        return AIMessage(content=response.content.strip())
    except Exception as e:
        print(f"[product_recommend] Gemini error: {e}")
        if language == "ar":
            error_message = "لم أجد عناصر مطابقة الآن."
        else:
            error_message = "No matching products found."
        return AIMessage(content=error_message)

def chat_greet(text: str, language: str = "en") -> AIMessage:
    """
    Generates a general chat or greeting response using the LLM.
    """
    prompt = CHAT_GREET_PROMPT.format(text=text, language=language)
    human_message = HumanMessage(content=prompt)
    chat_llm = get_chat_llm()
    response = chat_llm.invoke([human_message])
    
    # Return an AIMessage object instead of a string
    return AIMessage(content=response.content.strip())