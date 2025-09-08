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

def format_product_for_display(product: dict) -> str:
    """Format a product for display in the response"""
    title = product.get('title', 'Unknown Product')
    description = product.get('description', 'No description available')
    price = product.get('price', 'Price not available')
    currency = product.get('currency', 'AED')
    affiliate_url = product.get('affiliate_url', '')
    brand = product.get('brand', '')
    
    # Format the product display
    product_text = f"🛍️ **{title}**"
    if brand:
        product_text += f" by {brand}"
    
    product_text += f"\n💰 Price: {price} {currency}"
    product_text += f"\n📝 {description}"
    
    if affiliate_url:
        product_text += f"\n🔗 [View Product]({affiliate_url})"
    
    return product_text

def product_recommend(query: str, language: str = "en") -> AIMessage:
    """
    Searches for and formats a response with the top 5 product recommendations.
    """
    try:
        results = search_similar_products(query, top_k=5)
        
        if not results:
            if language == "ar":
                return AIMessage(content="عذراً، لم أجد منتجات مطابقة لطلبك.")
            else:
                return AIMessage(content="Sorry, I couldn't find any products matching your request.")
        
        # Format products for display
        formatted_products = []
        for i, product in enumerate(results, 1):
            formatted_products.append(f"{i}. {format_product_for_display(product)}")
        
        # Create the response
        if language == "ar":
            response_text = f"إليك {len(results)} منتجات قد تعجبك:\n\n" + "\n\n".join(formatted_products)
        else:
            response_text = f"Here are {len(results)} products you might like:\n\n" + "\n\n".join(formatted_products)
        
        return AIMessage(content=response_text)
        
    except Exception as e:
        print(f"[product_recommend] Error: {e}")
        if language == "ar":
            error_message = "عذراً، حدث خطأ في البحث عن المنتجات. يرجى المحاولة مرة أخرى."
        else:
            error_message = "Sorry, there was an error searching for products. Please try again."
        return AIMessage(content=error_message)

def chat_greet(text: str, language: str = "en") -> AIMessage:
    """
    Generates a general chat or greeting response using the LLM.
    """
    try:
        chat_llm = get_chat_llm()
        
        if language == "ar":
            prompt = f"أنت مساعد تسوق ذكي. رد على الرسالة التالية بطريقة ودودة ومفيدة: {text}"
        else:
            prompt = f"You are a smart shopping assistant. Respond to the following message in a friendly and helpful way: {text}"
        
        human_message = HumanMessage(content=prompt)
        response = chat_llm.invoke([human_message])
        
        return AIMessage(content=response.content.strip())
        
    except Exception as e:
        print(f"[chat_greet] Error: {e}")
        if language == "ar":
            return AIMessage(content="مرحباً! أنا مساعد التسوق الخاص بك. كيف يمكنني مساعدتك اليوم؟")
        else:
            return AIMessage(content="Hello! I'm your shopping assistant. How can I help you today?")