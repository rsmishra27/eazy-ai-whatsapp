import faiss
import numpy as np
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from app.core.embedding_model import embed_text, get_embedding_model
from app.core.s3_loader import S3ProductLoader

# Paths
INDEX_FILE = Path(__file__).parent.parent.parent / "data" / "faiss_index.bin"

# Global variables for lazy loading
_products = None
_index = None
_s3_loader = None
VECTOR_DIM = 384  # for 'all-MiniLM-L6-v2'

def get_s3_loader():
    """Get S3 loader instance"""
    global _s3_loader
    if _s3_loader is None:
        _s3_loader = S3ProductLoader()
    return _s3_loader

def get_products():
    """Lazy load products from S3"""
    global _products
    if _products is None:
        print("🔄 Loading products from S3...")
        s3_loader = get_s3_loader()
        _products = s3_loader.get_products()
        print(f"✅ Loaded {len(_products)} products from S3!")
    return _products

def get_index():
    """Lazy load or build FAISS index"""
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
    """Generate embeddings and save FAISS index"""
    print("⚙️ Rebuilding FAISS index from S3 products...")
    products = get_products()
    
    # Handle different product structures
    product_texts = []
    for p in products:
        # Try different field combinations
        title = p.get('title') or p.get('name') or p.get('name_en') or p.get('name_ar') or ''
        description = p.get('description') or p.get('details') or p.get('description_en') or p.get('description_ar') or ''
        category = p.get('category') or p.get('type') or ''
        brand = p.get('brand') or ''
        
        # Create searchable text
        product_text = f"{title} {description} {category} {brand}".strip()
        product_texts.append(product_text)
    
    print(f"🔄 Generating embeddings for {len(product_texts)} products...")
    
    # Process in batches to avoid memory issues
    batch_size = 1000
    product_embeddings = []
    
    for i in range(0, len(product_texts), batch_size):
        batch = product_texts[i:i + batch_size]
        print(f"🔄 Processing batch {i//batch_size + 1}/{(len(product_texts) + batch_size - 1)//batch_size}")
        
        batch_embeddings = [embed_text(t) for t in batch]
        product_embeddings.extend(batch_embeddings)
    
    product_embeddings = np.array(product_embeddings).astype("float32")
    
    index = faiss.IndexFlatL2(VECTOR_DIM)
    index.add(product_embeddings)
    
    INDEX_FILE.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_FILE))
    print(f"✅ Index rebuilt and saved with {len(products)} products.")
    return index

def search_similar_products(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
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