from sentence_transformers import SentenceTransformer

_model = None

def get_embedding_model():
    """Returns a singleton instance of the SentenceTransformer model."""
    global _model
    if _model is None:
        print("Loading SentenceTransformer model...")
        _model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("Model loaded.")
    return _model