from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from app.core.vector_search import search_similar_products
from app.core.prompts import CHAT_GREET_PROMPT, PRODUCT_RECOMMEND_PROMPT
from langchain.schema import HumanMessage, AIMessage

chat_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

@tool("product_recommend", args_schema={"query": str, "language": str})
def product_recommend(query: str, language: str = "en") -> AIMessage:
    """
    Searches for and formats a response with the top 3 product recommendations.
    This tool should be called after a 'product_recommend' intent is detected.
    """
    results = search_similar_products(query, top_k=3)
    
    prompt_text = PRODUCT_RECOMMEND_PROMPT.format(
        text=query,
        language=language,
        products=results
    )
    
    try:
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

@tool("chat_greet", args_schema={"text": str, "language": str})
def chat_greet(text: str, language: str = "en") -> AIMessage:
    """
    Generates a general chat or greeting response using the LLM.
    This tool is used for 'greet' and 'smalltalk' intents.
    """
    prompt = CHAT_GREET_PROMPT.format(text=text, language=language)
    human_message = HumanMessage(content=prompt)
    response = chat_llm.invoke([human_message])
    
    # Return an AIMessage object instead of a string
    return AIMessage(content=response.content.strip())