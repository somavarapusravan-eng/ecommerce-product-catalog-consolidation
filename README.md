# E-Commerce Product Catalog Consolidation

## 1. Project Overview

This project consolidates two independent e-commerce product catalogs, StyleHaus and UrbanThread, into a unified Gold product catalog using Snowflake and Python.

The objective is to identify duplicate products, standardize product information, resolve conflicting values, and expose the consolidated catalog through REST APIs.

## 2. Technology Stack

- Python
- Snowflake SQL
- Pandas
- RapidFuzz
- FastAPI
- Snowflake Connector for Python

## 3. Project Workflow

1. Ingest StyleHaus and UrbanThread CSV files into Snowflake.
2. Standardize product attributes into a common Silver table.
3. Generate potential duplicate candidates using string similarity.
4. Review candidate matches and confirm or reject them.
5. Store confirmed product mappings.
6. Consolidate records into the Gold product catalog.
7. Expose product search and retrieval through FastAPI.

## 4. Gold Catalog Consolidation

The Gold catalog contains one record per unique product.

Consolidation rules:

- Product name: Prefer the longer, more descriptive name.
- Description: Prefer the longer description.
- Price: Select the lowest available price.
- Other attributes: Select the most recently updated non-null value.
- Lineage: Maintain the source system for each selected field.

## 5. API Endpoints

### Health Check
`GET /`

Checks whether the API is running.

### Product Search
`GET /products/search?q=nike&limit=10`

Searches the Gold catalog by product name and returns matching products with relevance scores.

### Product Details
`GET /products/{product_id}`

Returns product details and field-level source lineage.

## 6. Running the Application

Install dependencies:

`pip install -r requirements.txt`

Configure Snowflake credentials in `.env`.

Start the API:

`uvicorn main:app --reload`

Open Swagger documentation:

`http://127.0.0.1:8000/docs`

## 7. Future Improvements

- Replace manual match review with an automated human-in-the-loop workflow.
- Introduce semantic embeddings for improved duplicate detection.
- Improve relevance ranking using a search engine or vector similarity.
- Add incremental processing for new and updated products.
- Optimize the pipeline for large catalogs containing millions of records.
- Add automated data quality checks and API tests.