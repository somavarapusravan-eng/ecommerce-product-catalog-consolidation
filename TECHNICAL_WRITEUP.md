# E-Commerce Product Catalog Consolidation
## Technical Approach and Implementation

### 1. Overview

The objective was to consolidate two independent e-commerce product catalogs, StyleHaus and UrbanThread, into a unified product catalog. The solution uses Snowflake for data ingestion, cleansing, standardization and consolidation, Python-based AI embeddings for duplicate candidate identification, and FastAPI for product search and retrieval.

The source datasets contained 164 records: 94 from StyleHaus and 70 from UrbanThread.

### 2. Architecture and Data Pipeline

The implementation follows a three-layer data architecture.

**Bronze Layer – Raw Ingestion**

Both source CSV files were loaded into separate Snowflake tables:
- `BRONZE.STYLEHAUS_RAW`
- `BRONZE.URBANTHREAD_RAW`

The original source records were retained for traceability.

**Silver Layer – Standardization**

Data from both sources was combined into a common schema in `SILVER.PRODUCTS_STANDARDIZED`.

Transformations included:
- Trimming unnecessary whitespace.
- Standardizing product names, brands and categories.
- Converting prices into numeric values.
- Standardizing timestamps and product attributes.
- Preserving source system and source product identifiers.

A matching view was also created with normalized product names, brands and categories.

**AI-Based Duplicate Detection**

The Snowflake trial account did not provide access to the required Cortex embedding functions. Therefore, local Python-based embeddings were used while Snowflake remained the primary data platform.

The Sentence Transformers model `all-MiniLM-L6-v2` generated 384-dimensional embeddings from product names, brands, categories, descriptions, colors, sizes and materials.

Cosine similarity was calculated between StyleHaus and UrbanThread products. A threshold of 0.70 was used to retrieve potential duplicate candidates.

This generated 92 candidate pairs from 6,580 cross-catalog comparisons.

Similarity scores were used for candidate discovery, not as automatic proof of duplication. Candidate pairs were reviewed and classified as CONFIRMED, REJECTED or PENDING.

The generated candidate pairs were reviewed and classified as CONFIRMED, REJECTED or PENDING.

Following the review process, 31 duplicate pairs were confirmed for consolidation. Only confirmed pairs were merged into the Gold catalog, while rejected and pending candidates were kept separate to prevent incorrect product merging.

The confirmed mappings were maintained separately and used during Gold catalog creation.

Only confirmed pairs were merged. Pending and rejected records were retained separately to avoid incorrect consolidation.

### 3. Gold Catalog and Merge Rules

The final consolidated table is:

`PRODUCT_CATALOG_DB.GOLD.PRODUCTS_GOLD`

The merge rules follow the assignment requirements:

| Attribute | Selection Rule |
|---|---|
| Product name | Longer descriptive name |
| Description | Longer description |
| Price | Lower available price |
| Other attributes | Most recently updated non-null value |

Field-level lineage was maintained through source columns such as `BRAND_SOURCE`, `PRICE_SOURCE`, `COLOR_SOURCE` and `DESCRIPTION_SOURCE`.

The final Gold catalog is expected to contain 133 unique products:
- 31 consolidated products, each combining one StyleHaus record and one UrbanThread record.
- 102 single-source products retained independently.

This represents the consolidation of 164 source records using 31 confirmed duplicate mappings.

### 4. API Implementation

FastAPI exposes the consolidated Gold catalog through two endpoints.

**Product Search**

`GET /products/search?q=nike`

Searches products by name and returns matching products with relevance scores.

**Product Details**

`GET /products/{product_id}`

Returns the product attributes, source record count, source systems and field-level lineage information.

The API was tested successfully using FastAPI Swagger documentation.

### 5. Trade-offs and Learnings

The embedding approach can identify similar products even when their names are written differently. However, semantic similarity alone can produce false positives, particularly for products with similar names but different models, sizes or colors.

Human review was therefore retained as a safeguard.

A limitation of the current implementation is that unresolved candidate pairs remain separate. This favors data accuracy over aggressive deduplication.

The trial-account restrictions also required embeddings to be generated locally rather than inside Snowflake.

### 6. Scaling the Solution to 10 Million Products

For a production-scale implementation, the following improvements would be considered:

- Use incremental ingestion instead of processing complete datasets repeatedly.
- Generate embeddings in batches and store them in a scalable vector index.
- Use approximate nearest-neighbor search to avoid comparing every possible product pair.
- Apply metadata filters such as brand, category and size before candidate matching.
- Use automated review queues for ambiguous matches.
- Monitor duplicate precision, recall, processing time and infrastructure cost.
- Use Snowflake's supported AI capabilities or a managed embedding service where available.

These changes would reduce unnecessary comparisons and improve throughput while preserving data lineage and reviewability.

### 7. Conclusion

The implementation demonstrates an end-to-end product catalog consolidation workflow combining Snowflake SQL transformations, AI-based duplicate candidate detection, controlled record merging, field-level lineage and REST API access.

The solution prioritizes accurate consolidation and traceability while providing a foundation for scaling to larger product catalogs.