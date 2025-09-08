from langchain.prompts import PromptTemplate

INTENT_PROMPT = PromptTemplate(
    input_variables=["text", "language"],
    template=(
        "Classify the intent of this WhatsApp message in {language}:\n"
        "{text}\n"
        "Possible intents: 'greet', 'product_recommend', 'smalltalk'.\n"
        "Only reply with the intent keyword."
    ),
)

CHAT_GREET_PROMPT = PromptTemplate(
    input_variables=["text", "language"],
    template=(
        "You are a helpful WhatsApp shopping assistant. Respond concisely in {language}.\n"
        "If the user greets you, introduce yourself as a shopping assistant and ask how you can help.\n"
        "User said: {text}"
    ),
)

PRODUCT_RECOMMEND_PROMPT = PromptTemplate(
    input_variables=["text", "language", "products"],
    template=(
        "You are a helpful product recommendation assistant. "
        "The user is looking for a product based on the query: '{text}'. "
        "The following products were found: {products}. "
        "Respond concisely in {language}, recommending the products in a friendly tone. "
        "Include product names, prices, and brief descriptions. "
        "If no products were found, apologize politely and suggest they try different keywords."
    ),
)

QUERY_EXTRACTION_PROMPT = PromptTemplate(
    input_variables=["text", "language"],
    template=(
        "Extract a concise product search query from the user's message in {language}. "
        "The query should contain key product characteristics like category, brand, price range, or features. "
        "Message: '{text}'. "
        "Only reply with the extracted query."
    ),
)