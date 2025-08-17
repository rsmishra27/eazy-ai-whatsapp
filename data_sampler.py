import pandas as pd

# Load the cleaned metadata
df = pd.read_csv("meta_Electronics_fixed.csv")

# Option 1: Most reviewed products (if you have reviews)
# df_subset = df[df['review_count'] >= 20].head(600)

# Option 2: Random sample across categories
df['main_category'] = df['categories'].apply(lambda x: eval(x)[-1][-1] if pd.notna(x) else None)
df_subset = df.groupby('main_category').apply(lambda x: x.sample(min(len(x), 20))).reset_index(drop=True)

# Keep around 500–600 products
df_subset = df_subset.head(600)

# Save subset
df_subset.to_csv("amazon_demo_subset.csv", index=False)
print("Subset saved with shape:", df_subset.shape)
