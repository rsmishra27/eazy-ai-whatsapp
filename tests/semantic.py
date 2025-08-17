# test_faiss_arabic.py
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

# ---------------------------
# Load the demo dataset and FAISS index
# ---------------------------
dataset_path = "electronics_demo_dataset.csv"
index_path = "electronics_demo_index.faiss"

df = pd.read_csv(dataset_path)
index = faiss.read_index(index_path)

# Load the multilingual embedding model
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# ---------------------------
# Define an Arabic query
# ---------------------------
query_ar = "سماعات بلوتوث لاسلكية"  # "wireless earbuds" in Arabic
vec = model.encode([query_ar], convert_to_numpy=True, dtype=np.float32)

# Search FAISS index
top_k = 5
distances, indices = index.search(vec, top_k)

print(f"Top {top_k} results for Arabic query: '{query_ar}'\n")

for rank, idx in enumerate(indices[0], start=1):
    product = df.iloc[idx]
    print(f"{rank}. {product['title']}")
    print(f"   Category: {product.get('main_category', '')}")
    desc = product.get('description', "")
    if pd.isna(desc):
        desc = ""
    print(f"   Description: {desc[:100]}...")
    print(f"   Image URL: {product.get('imUrl', '')}")
    print("-" * 50)
