
from fastapi import FastAPI, HTTPException, Query
from pipeline.connect_snowflake import get_snowflake_connection

app = FastAPI(
    title="Product Catalog API",
    description="Search and retrieve consolidated product catalog records",
    version="1.0.0"
)

TABLE = "PRODUCT_CATALOG_DB.GOLD.PRODUCTS_GOLD"


@app.get("/")
def home():
    return {"message": "Product Catalog API is running"}


@app.get("/products/search")
def search_products(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50)
):
    conn = get_snowflake_connection()

    try:
        cursor = conn.cursor()
        search_term = q.strip()

        sql = f"""
            SELECT
                PRODUCT_ID,
                PRODUCT_NAME,
                BRAND,
                CATEGORY,
                PRICE,
                CASE
                    WHEN LOWER(PRODUCT_NAME) = LOWER(%s) THEN 1.0
                    WHEN LOWER(PRODUCT_NAME) LIKE LOWER(%s) THEN 0.9
                    ELSE 0.7
                END AS RELEVANCE
            FROM {TABLE}
            WHERE PRODUCT_NAME ILIKE %s
            ORDER BY RELEVANCE DESC, PRODUCT_NAME
            LIMIT %s
        """

        cursor.execute(
            sql,
            (
                search_term,
                search_term + "%",
                "%" + search_term + "%",
                limit
            )
        )

        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return {
            "query": search_term,
            "count": len(results),
            "results": results
        }

    finally:
        conn.close()


@app.get("/products/{product_id}")
def get_product(product_id: str):
    conn = get_snowflake_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            f"""
            SELECT *
            FROM {TABLE}
            WHERE PRODUCT_ID = %s
            """,
            (product_id,)
        )

        row = cursor.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        columns = [col[0] for col in cursor.description]
        product = dict(zip(columns, row))

        return {
            "product": product,
            "lineage": {
                "product_name": "Selected from the source with the longest name",
                "description": "Selected from the source with the longest description",
                "price": "Lowest available source price",
                "other_fields": "Most recently updated non-null source value",
                "field_source_columns": [
                    "BRAND_SOURCE",
                    "CATEGORY_SOURCE",
                    "DESCRIPTION_SOURCE",
                    "PRICE_SOURCE",
                    "COLOR_SOURCE",
                    "SIZE_SOURCE",
                    "MATERIAL_SOURCE",
                    "IN_STOCK_SOURCE"
                ]
            }
        }

    finally:
        conn.close()
