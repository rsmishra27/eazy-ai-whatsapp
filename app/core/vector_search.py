import faiss
import numpy as np
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from app.core.embedding_model import embed_text, get_embedding_model

# Paths
PRODUCTS_FILE = Path(__file__).parent / "products.json"
INDEX_FILE = Path(__file__).parent.parent.parent / "data" / "faiss_index.bin"

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
        
        if INDEX_FILE.exists():
            print("🔄 Loading existing FAISS index from disk...")
            _index = faiss.read_index(str(INDEX_FILE))
            
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
    
    # Handle multilingual product structure
    product_texts = []
    for p in products:
        # Use English fields if available, fallback to Arabic or generic fields
        name = p.get('name_en') or p.get('name_ar') or p.get('name', '')
        description = p.get('description_en') or p.get('description_ar') or p.get('description', '')
        product_texts.append(f"{name} - {description}")
    
    product_embeddings = np.array([embed_text(t) for t in product_texts]).astype("float32")
    index = faiss.IndexFlatL2(VECTOR_DIM)
    index.add(product_embeddings)
    
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_FILE))
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

# For compatibility with the other developer's code
async def initialize_vector_store():
    """Initializes or loads the FAISS index."""
    get_index()
    get_products()