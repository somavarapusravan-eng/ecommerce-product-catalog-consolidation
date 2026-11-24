
import pandas as pd
import pickle
import snowflake.connector
from sentence_transformers import SentenceTransformer

# Connect using your existing Snowflake connection
from connect_snowflake import get_snowflake_connection

conn = get_snowflake_connection()

query = """
SELECT
    SOURCE_SYSTEM,
    SOURCE_PRODUCT_ID,
    PRODUCT_NAME,
    BRAND,
    CATEGORY,
    DESCRIPTION,
    COLOR,
    SIZE,
    MATERIAL
FROM PRODUCT_CATALOG_DB.SILVER.PRODUCT_MATCHING
"""

df = pd.read_sql(query, conn)

print("Products retrieved:", len(df))

# Load the local AI embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Combine product details into one text field
df["PRODUCT_TEXT"] = (
    df["PRODUCT_NAME"].fillna("") + " " +
    df["BRAND"].fillna("") + " " +
    df["CATEGORY"].fillna("") + " " +
    df["DESCRIPTION"].fillna("") + " " +
    df["COLOR"].fillna("") + " " +
    df["SIZE"].fillna("") + " " +
    df["MATERIAL"].fillna("")
)

# Generate AI embeddings
embeddings = model.encode(
    df["PRODUCT_TEXT"].tolist(),
    normalize_embeddings=True,
    show_progress_bar=True
)

# Save products and their embeddings
with open("data/product_embeddings.pkl", "wb") as file:
    pickle.dump(
        {"products": df, "embeddings": embeddings},
        file
    )

print("Embedding generation completed.")
print("Embedding dimensions:", embeddings.shape)
