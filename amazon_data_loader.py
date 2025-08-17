import os
import gzip
import json
import requests
import pandas as pd

# -----------------------------
# URLs (Stanford SNAP mirror)
# -----------------------------
reviews_url = "http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/reviews_Electronics_5.json.gz"
meta_url = "http://snap.stanford.edu/data/amazon/productGraph/categoryFiles/meta_Electronics.json.gz"

reviews_file = "reviews_Electronics_5.json.gz"
meta_file = "meta_Electronics.json.gz"

def download_file(url, filename):
    if not os.path.exists(filename):
        print(f"Downloading {filename} ...")
        response = requests.get(url, stream=True)
        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded {filename}!")

def load_json_gz(path, max_records=None):
    data = []
    with gzip.open(path, "rb") as f:
        for i, line in enumerate(f):
            if max_records and i >= max_records:
                break
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return data

# -----------------------------
# Step 1: Download
# -----------------------------
download_file(reviews_url, reviews_file)
download_file(meta_url, meta_file)

# -----------------------------
# Step 2: Load reviews
# -----------------------------
print("Loading reviews...")
reviews = load_json_gz(reviews_file)
df_reviews = pd.DataFrame(reviews)

df_reviews = df_reviews[["reviewerID", "asin", "overall", "reviewText"]].dropna()
df_reviews = df_reviews.rename(columns={
    "reviewerID": "user_id",
    "asin": "product_id",
    "overall": "rating",
    "reviewText": "review"
})

print(f"Total reviews loaded: {len(df_reviews)}")

# -----------------------------
# Step 3: Load metadata
# -----------------------------
print("Loading metadata...")
meta = load_json_gz(meta_file)
df_meta = pd.DataFrame(meta)

df_meta = df_meta[["asin", "title", "description", "categories", "brand"]]
df_meta = df_meta.rename(columns={"asin": "product_id"})

# -----------------------------
# Step 4: Merge
# -----------------------------
df = df_reviews.merge(df_meta, on="product_id", how="left")

# -----------------------------
# Step 5: Filter to ~600 products
# -----------------------------
product_counts = df["product_id"].value_counts()
selected_products = product_counts[product_counts >= 20].head(600).index
filtered_df = df[df["product_id"].isin(selected_products)]

print(f"Selected {filtered_df['product_id'].nunique()} products with {len(filtered_df)} reviews")

# -----------------------------
# Step 6: Save
# -----------------------------
filtered_df.to_csv("amazon_electronics_subset.csv", index=False)
print("Final subset saved to amazon_electronics_subset.csv")
