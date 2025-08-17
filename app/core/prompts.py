from langchain.prompts import PromptTemplate

# Intent detection prompt template
INTENT_PROMPT = PromptTemplate(
    input_variables=["text", "language"],
    template=(
        "Classify the intent of this WhatsApp message in {language}:\n"
        "{text}\n"
        "Possible intents: 'greet', 'product_recommend', 'smalltalk'.\n"
        "Only reply with the intent keyword."
    ),
)

# Chat/Greet prompt template
CHAT_GREET_PROMPT = PromptTemplate(
    input_variables=["text", "language"],
    template=(
        "You are a helpful WhatsApp assistant. Respond concisely in {language}.\n"
        "User said: {text}"
    ),
)
