
import pickle
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Load generated embeddings
with open("data/product_embeddings.pkl", "rb") as file:
    saved = pickle.load(file)

df = saved["products"]
embeddings = saved["embeddings"]

# Separate products by source brand
stylehaus_idx = df.index[df["SOURCE_SYSTEM"] == "STYLEHAUS"].tolist()
urbanthread_idx = df.index[df["SOURCE_SYSTEM"] == "URBANTHREAD"].tolist()

# Compare every StyleHaus product with every UrbanThread product
similarity_matrix = cosine_similarity(
    embeddings[stylehaus_idx],
    embeddings[urbanthread_idx]
)

matches = []

for i, style_idx in enumerate(stylehaus_idx):
    for j, urban_idx in enumerate(urbanthread_idx):

        style = df.loc[style_idx]
        urban = df.loc[urban_idx]

        score = float(similarity_matrix[i, j])

        # Keep plausible candidates for review
        if score >= 0.70:
            matches.append({
                "STYLEHAUS_ID": style["SOURCE_PRODUCT_ID"],
                "URBANTHREAD_ID": urban["SOURCE_PRODUCT_ID"],
                "STYLEHAUS_NAME": style["PRODUCT_NAME"],
                "URBANTHREAD_NAME": urban["PRODUCT_NAME"],
                "STYLEHAUS_BRAND": style["BRAND"],
                "URBANTHREAD_BRAND": urban["BRAND"],
                "STYLEHAUS_COLOR": style["COLOR"],
                "URBANTHREAD_COLOR": urban["COLOR"],
                "STYLEHAUS_SIZE": style["SIZE"],
                "URBANTHREAD_SIZE": urban["SIZE"],
                "SIMILARITY_SCORE": round(score, 4)
            })

result = pd.DataFrame(matches)

if not result.empty:
    result = result.sort_values(
        "SIMILARITY_SCORE", ascending=False
    )

result.to_csv("data/ai_match_candidates.csv", index=False)

print("Total comparisons:", similarity_matrix.size)
print("Potential duplicate pairs:", len(result))
print("Saved: data/ai_match_candidates.csv")
