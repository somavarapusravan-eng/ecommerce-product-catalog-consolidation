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

## 3. Architecture & Workflow

The project follows a multi-stage data pipeline:

1. Ingest raw product data from StyleHaus and UrbanThread.
2. Standardize product attributes into a common Silver layer.
3. Generate potential duplicate candidates using string similarity.
4. Review candidate matches and confirm or reject duplicates.
5. Store confirmed product mappings.
6. Consolidate products into a unified Gold catalog.
7. Expose the Gold catalog through REST APIs.

## 4. Project Execution Guide

Execute the scripts in the following order.

### Step 1: Snowflake Setup

Run the SQL scripts in Snowflake in the specified order.

| Sequence | Script | Purpose |
|---|---|---|
| 1 | `sql/01_setup.sql` | Create database, schemas, tables, stages and initial objects |
| 2 | `sql/02_standardization.sql` | Standardize source product data and populate the Silver layer |
| 3 | `sql/03_matching.sql` | Prepare data and candidate matching structures |

> Execute each SQL script completely before proceeding to the next step.

### Step 2: Python Data Processing

Open the project in Visual Studio Code and configure the Python environment.

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure the Snowflake connection using the `.env` file.

Execute the Python scripts in the following order:

1. Candidate matching and similarity scoring.
2. Match review and validation.
3. Confirmed mapping generation and processing.

Review the generated match results and ensure that duplicate mappings are validated before proceeding.

### Step 3: Final Gold Catalog Creation

After completing the Python matching and validation process, execute:

`sql/04_gold_consolidation.sql`

This script consolidates the validated product mappings and source records into the final Gold product catalog.

### Step 4: Start the REST API

Once the Gold catalog has been created successfully, start the FastAPI application.

```bash
uvicorn main:app --reload
```

API documentation:

http://127.0.0.1:8000/docs

## 5. Gold Catalog Consolidation

The Gold catalog contains one record per unique product.

### Consolidation Rules

- **Product name:** Prefer the longer, more descriptive name.
- **Description:** Prefer the longer description.
- **Price:** Select the lowest available price.
- **Other attributes:** Select the most recently updated non-null value.
- **Lineage:** Maintain the source system for each selected field.

## 6. API Endpoints

### Health Check

`GET /`

Checks whether the API is running.

### Product Search

`GET /products/search?q=nike&limit=10`

Searches the Gold catalog by product name and returns matching products with relevance scores.

### Product Details

`GET /products/{product_id}`

Returns product details and field-level source lineage.

## 7. Configuration

Before running the project, configure the required Snowflake connection details in the `.env` file.

Ensure that:

- Snowflake credentials are valid.
- Required database objects are created.
- Python dependencies are installed.
- The product matching review is completed before Gold consolidation.

## 8. Expected Outcome

The pipeline produces a unified product catalog with:

- Duplicate products identified across source systems.
- Validated product mappings.
- Standardized product attributes.
- Consolidated product records.
- Field-level source lineage.
- REST API access for searching and retrieving products.