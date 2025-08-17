import json
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import faiss
from app.core.embedding_model import get_embedding_model

PRODUCTS_FILE = Path(__file__).parent / "products.json"
INDEX_FILE = Path(__file__).parent.parent.parent / "data" / "faiss_index.bin"
_index = None
_products: List[Dict[str, Any]] = []

async def initialize_vector_store():
    """Initializes or loads the FAISS index."""
    global _index, _products
    model = get_embedding_model()

    if INDEX_FILE.exists():
        print("Loading existing FAISS index...")
        _index = faiss.read_index(str(INDEX_FILE))
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            _products = json.load(f)
    else:
        print("Creating new FAISS index...")
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            _products = json.load(f)
        
        product_descriptions = [p["description_en"] for p in _products]
        embeddings = model.encode(product_descriptions, convert_to_tensor=False)
        embeddings = np.array(embeddings).astype('float32')

        dimension = embeddings.shape[1]
        _index = faiss.IndexFlatL2(dimension)
        _index.add(embeddings)
        
        INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
        faiss.write_index(_index, str(INDEX_FILE))
        print("FAISS index created and saved.")

def search_similar_products(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Performs a semantic search on the FAISS index."""
    if _index is None or not _products:
        print("Vector store not initialized.")
        return []

    model = get_embedding_model()
    query_embedding = model.encode([query], convert_to_tensor=False)
    query_embedding = np.array(query_embedding).astype('float32')
    
    D, I = _index.search(query_embedding, top_k)
    
    results = [_products[idx] for idx in I[0] if idx < len(_products)]
    return results