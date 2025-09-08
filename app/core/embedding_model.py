# app/core/embedding_model.py

from sentence_transformers import SentenceTransformer

# Global variable to store the model (lazy loaded)
_model = None

def get_model():
    """Lazy load the embedding model to avoid blocking startup."""
    global _model
    if _model is None:
        print("🔄 Loading embedding model...")
        _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("✅ Embedding model loaded successfully!")
    return _model

def embed_text(text: str):
    """
    Convert the input text into a dense vector embedding using the 
    multilingual MiniLM model.
    Works for Arabic, English, and many other languages.
    """
    model = get_model()
    return model.encode(text, convert_to_numpy=True)
