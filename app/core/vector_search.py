import faiss
import numpy as np
import json
import os
from app.core.embedding_model import embed_text

# Paths
PRODUCTS_FILE = "app/core/products.json"
INDEX_FILE = "app/core/products.index"

# Global variables for lazy loading
_products = None
_index = None
VECTOR_DIM = 384  # for 'all-MiniLM-L6-v2'

def get_products():
    """Lazy load products from JSON file."""
    global _products
    if _products is None:
        print("🔄 Loading products from JSON...")
        with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
            _products = json.load(f)
        print(f"✅ Loaded {len(_products)} products!")
    return _products

def get_index():
    """Lazy load or build FAISS index."""
    global _index
    if _index is None:
        print("🔄 Loading FAISS index...")
        products = get_products()
        
        if os.path.exists(INDEX_FILE):
            print("🔄 Loading existing FAISS index from disk...")
            _index = faiss.read_index(INDEX_FILE)
            
            # Check if catalog size changed
            if _index.ntotal != len(products):
                print("⚠️ Product count changed — rebuilding index...")
                _index = build_and_save_index()
        else:
            _index = build_and_save_index()
        print("✅ FAISS index loaded successfully!")
    return _index

def build_and_save_index():
    """
    Generate embeddings from products.json and save FAISS index to disk.
    """
    print("⚙️ Rebuilding FAISS index from products.json...")
    products = get_products()
    product_texts = [f"{p['name']} - {p['description']}" for p in products]
    product_embeddings = np.array([embed_text(t) for t in product_texts]).astype("float32")
    index = faiss.IndexFlatL2(VECTOR_DIM)
    index.add(product_embeddings)
    faiss.write_index(index, INDEX_FILE)
    print(f"✅ Index rebuilt and saved with {len(products)} products.")
    return index

def search_similar_products(query: str, top_k: int = 3):
    """
    Search for the most semantically similar products to the query.
    """
    index = get_index()
    products = get_products()
    query_vec = embed_text(query).astype("float32").reshape(1, -1)
    distances, indices = index.search(query_vec, top_k)
    return [products[i] for i in indices[0]]
