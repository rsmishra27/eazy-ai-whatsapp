# app/core/embedding_model.py
from sentence_transformers import SentenceTransformer

# Load a multilingual embedding model that supports Arabic and English well
model = SentenceTransformer('all-MiniLM-L6-v2')  # Lightweight, multilingual model

def embed_text(text: str):
    """
    Convert input text to dense vector embedding.
    """
    return model.encode(text, convert_to_numpy=True)
