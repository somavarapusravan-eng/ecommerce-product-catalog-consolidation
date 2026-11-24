# E-Commerce Product Catalog Consolidation
## Technical Approach & Implementation

### 1. Problem Understanding and Approach

The objective of this project was to consolidate product information from two independent e-commerce catalogs, StyleHaus and UrbanThread, into a unified product catalog.

I approached the problem as a data integration and entity resolution problem rather than simply combining two datasets. Since the same product can exist across both catalogs with differences in naming conventions, descriptions, attributes and pricing, a direct merge could result in duplicate records or incorrect consolidation.

My approach was to separate the process into four major stages:

1. Ingest and standardize the source data.
2. Identify potential duplicate products using similarity-based matching.
3. Validate matches before consolidating records.
4. Build a unified Gold catalog and expose it through APIs.

This separation allowed me to preserve the original data, independently validate matching decisions and control how records were merged.

### 2. Data Ingestion and Standardization

The two source datasets contained 164 records, with 94 products from StyleHaus and 70 from UrbanThread.

I first loaded the source files into separate Snowflake Bronze tables, retaining the original records and source identifiers. I wanted to preserve the raw data so that any transformation or matching decision could be traced back to the original source.

From there, I created a common Silver data structure to align both catalogs.

The standardization process included:

- Trimming whitespace and cleaning inconsistent text values.
- Normalizing product names, brands and categories.
- Converting price fields into consistent numeric formats.
- Standardizing product attributes and timestamps.
- Preserving source system identifiers and metadata.

I also created normalized matching attributes to reduce unnecessary differences caused by formatting, casing or inconsistent naming conventions.

The purpose of this step was to ensure that the matching process operated on consistent data rather than raw, inconsistent source values.

### 3. Product Matching and Duplicate Identification

One of the main challenges was identifying the same product across two catalogs when the product names or descriptions were not exactly identical.

Instead of relying only on exact string matching, I implemented a semantic similarity-based approach using Python and Sentence Transformers.

I used the `all-MiniLM-L6-v2` model to generate 384-dimensional embeddings from product information, including names, brands, categories, descriptions and available attributes.

I then calculated cosine similarity between StyleHaus and UrbanThread products to identify potentially matching records.

Since the catalogs were relatively small, I evaluated all cross-catalog combinations. This resulted in 6,580 comparisons.

I applied a similarity threshold of 0.70 to identify potential matching candidates. This threshold was used to narrow down the records requiring further review, rather than automatically merging products.

The process generated 92 candidate pairs.

I deliberately separated candidate identification from the final consolidation decision because products can have similar descriptions but still represent different models, sizes, colors or variants.

### 4. Match Validation and Data Quality Control

I did not treat similarity scores as definitive proof that two products were identical.

The generated candidates were exported for review and classified as:

- CONFIRMED
- REJECTED
- PENDING

During validation, I reviewed the product attributes and candidate information to determine whether the records represented the same product.

For example, products with similar names but different sizes, colors or model identifiers could be false positives. These should remain separate records rather than being merged based on similarity alone.

Out of the generated candidates, 31 product pairs were confirmed as duplicates.

I maintained the confirmed mappings separately from the source product tables. This allowed the consolidation logic to use only validated mappings and prevented rejected or unresolved candidates from being merged accidentally.

This approach prioritizes catalog accuracy over aggressive deduplication.

### 5. Gold Catalog Consolidation

After validating the duplicate mappings, I created the final consolidated catalog in the Snowflake Gold layer:

`PRODUCT_CATALOG_DB.GOLD.PRODUCTS_GOLD`

The consolidation logic was designed to produce one record per unique product while retaining relevant source information.

For confirmed duplicate pairs, I applied attribute-level selection rules:

| Attribute | Consolidation Rule |
|---|---|
| Product name | Select the longer, more descriptive name |
| Description | Select the more informative description based on length |
| Price | Select the lowest available price |
| Other attributes | Select the most recently updated non-null value |

I applied the selection rules at the field level rather than choosing one entire source record as the winner. This allowed the consolidated record to retain the most useful information from both catalogs.

I also implemented field-level source lineage through columns such as `BRAND_SOURCE`, `PRICE_SOURCE`, `COLOR_SOURCE` and `DESCRIPTION_SOURCE`.

This provides visibility into where each selected attribute originated and makes the consolidated data easier to audit.

The expected final catalog consists of 133 unique products:

- 31 consolidated products representing confirmed duplicates across both catalogs.
- 102 products retained as independent records.

This reconciles the original 164 records with the 31 confirmed product consolidations.

### 6. API Layer and Data Access

Once the Gold catalog was created, I exposed it through a REST API using FastAPI.

I implemented two primary endpoints.

**Product Search**

`GET /products/search?q=nike&limit=10`

This endpoint allows users to search the catalog by product name and retrieve matching products with relevance scores.

**Product Details**

`GET /products/{product_id}`

This endpoint retrieves an individual product along with its consolidated attributes, source record information and field-level lineage.

I used FastAPI to provide a lightweight service layer over the Snowflake Gold catalog, making the consolidated data accessible without requiring consumers to query Snowflake directly.

I also used the Swagger interface for endpoint validation and testing.

### 7. Challenges and Engineering Decisions

**Semantic matching instead of exact matching**

Exact matching would have missed products with differences in naming conventions, descriptions or formatting. Semantic embeddings provided a better way to identify potential matches across independently maintained catalogs.

**Local embeddings instead of Snowflake Cortex**

The Snowflake trial environment did not provide access to the required Cortex embedding functionality. Rather than blocking the implementation, I generated embeddings locally using Sentence Transformers and retained Snowflake as the primary platform for ingestion, transformation and consolidation.

**Human validation instead of automatic merging**

Similarity scores can produce false positives. I introduced a review step to validate candidate pairs before consolidation, reducing the risk of incorrectly merging distinct products.

**Field-level consolidation instead of source-level selection**

Selecting one source record entirely could result in losing useful attributes from the other source. I used attribute-level selection rules to combine the best available values while maintaining field-level lineage.

### 8. Scalability and Production Considerations

The current implementation evaluates all cross-catalog product combinations, which is reasonable for the provided dataset of 164 records.

For a production dataset containing millions of products, I would avoid exhaustive pairwise comparisons and introduce a scalable candidate generation strategy.

Potential improvements include:

- Incremental ingestion and processing of changed products only.
- Batch embedding generation.
- Candidate blocking using brand, category or other product attributes.
- Approximate nearest-neighbor search using a vector index.
- Hybrid matching combining semantic similarity, exact identifiers and attribute-level comparisons.
- Confidence-based automated matching for high-confidence candidates.
- Review queues for ambiguous matches.
- Monitoring matching precision, recall, false positives, processing time and cost.

I would also make the pipeline incremental and idempotent, ensuring that rerunning it does not create duplicate mappings or duplicate Gold records.

### 9. Conclusion

I designed the solution to address the complete product consolidation lifecycle, from ingestion and standardization to duplicate identification, validation, consolidation and API consumption.

The key design decision was to treat similarity matching as a candidate discovery mechanism and not as an automatic merge decision.

By combining Snowflake-based data processing, Python semantic matching, controlled validation, field-level consolidation and source lineage, the solution produces a unified catalog while minimizing the risk of incorrect product merges.

The implementation also provides a foundation for extending the matching and consolidation process to larger datasets and production workloads.