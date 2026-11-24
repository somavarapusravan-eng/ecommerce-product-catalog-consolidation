
import pandas as pd

df = pd.read_csv("data/ai_match_candidates.csv")

df["REVIEW_DECISION"] = "PENDING"
df["REVIEW_NOTES"] = ""

df = df.sort_values("SIMILARITY_SCORE", ascending=False)

df.to_csv("data/match_review.csv", index=False)

print("Review file created:", len(df), "pairs")
print(df.head(10).to_string(index=False))
