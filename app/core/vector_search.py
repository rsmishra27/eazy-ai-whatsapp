# app/core/vector_search.py
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

VECTOR_DIM = 384  # for paraphrase-multilingual-MiniLM-L12-v2


def build_and_save_index():
    """
    Generate embeddings from products.json (both EN + AR text) and save FAISS index.
    """
    print("⚙️ Rebuilding FAISS index from products.json...")

    product_texts = []
    expanded_products = []

    for p in products:
        # English entry
        if p.get("name_en") and p.get("desc_en"):
            product_texts.append(f"{p['name_en']} - {p['desc_en']}")
            expanded_products.append(p)

        # Arabic entry
        if p.get("name_ar") and p.get("desc_ar"):
            product_texts.append(f"{p['name_ar']} - {p['desc_ar']}")
            expanded_products.append(p)

    product_embeddings = np.array([embed_text(t) for t in product_texts]).astype("float32")

    index = faiss.IndexFlatL2(VECTOR_DIM)
    index.add(product_embeddings)
    faiss.write_index(index, INDEX_FILE)

    print(f"✅ Index rebuilt and saved with {len(expanded_products)} entries.")
    return index, expanded_products


# --- Load or Rebuild ---
if os.path.exists(INDEX_FILE):
    print("🔄 Loading existing FAISS index from disk...")
    index = faiss.read_index(INDEX_FILE)

    # if index size != product entries * 2 (en+ar), rebuild
    expected_size = sum(1 for p in products for f in ["name_en", "name_ar"] if p.get(f))
    if index.ntotal != expected_size:
        print("⚠️ Product count changed — rebuilding index...")
        index, products_expanded = build_and_save_index()
    else:
        products_expanded = products
else:
    index, products_expanded = build_and_save_index()


def search_similar_products(query: str, top_k: int = 3):
    """
    Search for the most semantically similar products to the query.
    """
    query_vec = embed_text(query).astype("float32").reshape(1, -1)
    distances, indices = index.search(query_vec, top_k)

    results = []
    for i in indices[0]:
        if i < len(products_expanded):
            results.append(products_expanded[i])
    return results
