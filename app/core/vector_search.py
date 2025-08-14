import faiss
import numpy as np
import json
import os
from app.core.embedding_model import embed_text

# Paths
PRODUCTS_FILE = "app/core/products.json"
INDEX_FILE = "app/core/products.index"

# Load products from JSON
with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
    products = json.load(f)

VECTOR_DIM = 384  # for 'all-MiniLM-L6-v2'


def build_and_save_index():
    """
    Generate embeddings from products.json and save FAISS index to disk.
    """
    print("⚙️ Rebuilding FAISS index from products.json...")
    product_texts = [f"{p['name']} - {p['description']}" for p in products]
    product_embeddings = np.array([embed_text(t) for t in product_texts]).astype("float32")
    index = faiss.IndexFlatL2(VECTOR_DIM)
    index.add(product_embeddings)
    faiss.write_index(index, INDEX_FILE)
    print(f"✅ Index rebuilt and saved with {len(products)} products.")
    return index


# --- Load or Rebuild ---
if os.path.exists(INDEX_FILE):
    print("🔄 Loading existing FAISS index from disk...")
    index = faiss.read_index(INDEX_FILE)

    # Check if catalog size changed
    if index.ntotal != len(products):
        print("⚠️ Product count changed — rebuilding index...")
        index = build_and_save_index()
else:
    index = build_and_save_index()


def search_similar_products(query: str, top_k: int = 3):
    """
    Search for the most semantically similar products to the query.
    """
    query_vec = embed_text(query).astype("float32").reshape(1, -1)
    distances, indices = index.search(query_vec, top_k)
    return [products[i] for i in indices[0]]
