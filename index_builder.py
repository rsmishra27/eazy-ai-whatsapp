import pandas as pd
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# ---------------------------
# Step 1: Load subset
# ---------------------------
subset_file = "amazon_demo_subset.csv"
df = pd.read_csv(subset_file)

# Combine title + description + category for embeddings
df['text'] = df['title'].fillna('') + " " + df['description'].fillna('') + " " + df['main_category'].fillna('')

# ---------------------------
# Step 2: Load embedding model
# ---------------------------
print("Loading embedding model...")
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# ---------------------------
# Step 3: Generate embeddings
# ---------------------------
print("Generating embeddings...")
embeddings = model.encode(df['text'].tolist(), batch_size=32, show_progress_bar=True)
embeddings = np.array(embeddings, dtype='float32')

# ---------------------------
# Step 4: Build FAISS index
# ---------------------------
print("Building FAISS index...")
d = embeddings.shape[1]
index = faiss.IndexFlatL2(d)
index.add(embeddings)

print("Total vectors in index:", index.ntotal)

# ---------------------------
# Step 5: Save index + metadata
# ---------------------------
faiss.write_index(index, "electronics_demo_index.faiss")
df.to_csv("electronics_demo_dataset.csv", index=False)

print("✅ Saved electronics_demo_index.faiss and electronics_demo_dataset.csv")
