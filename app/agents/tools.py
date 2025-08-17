from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from app.core.vector_search import search_similar_products
from app.core.prompts import CHAT_GREET_PROMPT
from langchain.schema import HumanMessage

chat_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)

@tool("product_recommend", args_schema={"query": str, "language": str})
def product_recommend(query: str, language: str = "en") -> str:
    results = search_similar_products(query, top_k=3)
    if not results:
        return "لم أجد عناصر مطابقة الآن." if language == "ar" else "No matching products found."
    if language == "ar":
        lines = ["اقتراحات تناسبك:"]
        for p in results:
            lines.append(f"- {p.get('name_ar', p.get('name_en'))} – {p.get('price')} {p.get('currency', '')}")
    else:
        lines = ["Here are some picks:"]
        for p in results:
            lines.append(f"- {p.get('name_en', p.get('name_ar'))} – {p.get('price')} {p.get('currency', '')}")
    return "\n".join(lines)

@tool("chat_greet", args_schema={"text": str, "language": str})
def chat_greet(text: str, language: str = "en") -> str:
    prompt = CHAT_GREET_PROMPT.format(text=text, language=language)
    human_message = HumanMessage(content=prompt)
    response = chat_llm.invoke([human_message])
    return response.content.strip()
