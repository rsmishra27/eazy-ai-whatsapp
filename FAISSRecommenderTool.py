import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class FAISSRecommenderTool:
    def __init__(self, index_path: str, metadata_csv: str):
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        
        # Load product metadata
        self.df = pd.read_csv(metadata_csv)
        
        # Load multilingual embedding model
        self.model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    def recommend(self, query: str, top_k: int = 5):
        # Encode query
        query_vec = self.model.encode([query], convert_to_numpy=True).astype("float32")
        
        # Search FAISS index
        distances, indices = self.index.search(query_vec, top_k)
        
        results = []
        for idx in indices[0]:
            product = self.df.iloc[idx]
            results.append({
                "title": product["title"],
                "description": product["description"],
                "price": product.get("price", "N/A"),
                "image": product.get("imUrl", "")
            })
        return results
