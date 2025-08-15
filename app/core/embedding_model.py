# app/core/embedding_model.py

from sentence_transformers import SentenceTransformer

# Load a strong multilingual embedding model that works well with Arabic
# This model is trained on multiple languages including Arabic and English
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def embed_text(text: str):
    """
    Convert the input text into a dense vector embedding using the 
    multilingual MiniLM model.
    Works for Arabic, English, and many other languages.
    """
    return model.encode(text, convert_to_numpy=True)
