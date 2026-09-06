# Analytical Data Model Architecture

**Project:** Gradient Learnings Data Analytics Hackathon 2026 (Olist)
**Module:** 2 -- Data Model and Join Architecture
**Author:** Automated Pipeline
**Grain:** 1 row = 1 order_id (99,441 rows)

---

## 1. Architecture Overview

The analytical data model follows a **layered architecture** that transforms
nine raw CSV source files into a single, validated, analysis-ready table.

```
Layer A: Raw Sources           9 CSVs (untouched, read-only)
    |
Layer B: Pre-Aggregations      items_agg, payments_agg, reviews_selected
    |                          (each collapsed to 1 row per order_id)
Layer C: Reference Tables      zip_centroids, category_translation
    |
Layer D: Canonical Order Base  99,441 rows x 52 cols
    |                          (validated joins, population flags, financial diagnostics)
Layer E: Missingness Flags     +9 boolean availability indicators
    |
Layer F: Analytical Features   +8 derived flags and computed metrics
    |
Layer G: Temporal Features     +13 date-derived dimensions
    |
Layer H: Final Analytical      99,441 rows x 80 cols
         Model                 (all layers merged, contract-validated)
```

**Design Principle:** Every downstream module (Module 3+) consumes Layer H.
No module should ever access raw files or intermediate aggregations directly.

---

## 2. Layer Definitions

### Layer A -- Raw Sources

| Table | File | Rows | Key |
|-------|------|------|-----|
| Orders | olist_orders_dataset.csv | 99,441 | order_id |
| Items | olist_order_items_dataset.csv | 112,650 | (order_id, order_item_id) |
| Payments | olist_order_payments_dataset.csv | 103,886 | (order_id, payment_sequential) |
| Reviews | olist_order_reviews_dataset.csv | 99,224 | (review_id, order_id) |
| Customers | olist_customers_dataset.csv | 99,441 | customer_id |
| Products | olist_products_dataset.csv | 32,951 | product_id |
| Sellers | olist_sellers_dataset.csv | 3,095 | seller_id |
| Geolocation | olist_geolocation_dataset.csv | 1,000,163 | none (multi-row per zip) |
| Translation | product_category_name_translation.csv | 71 | product_category_name |

Raw files are **never modified**. All transformations operate on in-memory copies.

### Layer B -- Pre-Aggregated Components

These modules collapse multi-row source tables to order-grain:

| Component | Module | Output Rows | Aggregation Strategy |
|-----------|--------|-------------|---------------------|
| Items Aggregated | `src/item_aggregation.py` | 98,666 | Sum prices, count items, select dominant category/seller |
| Payments Aggregated | `src/payment_aggregation.py` | 99,440 | Sum values, count lines, select dominant payment type |
| Reviews Selected | `src/review_aggregation.py` | 98,673 | Latest valid review per order (timestamp-based) |

**Fan-out Prevention:** Each aggregation produces exactly 1 row per order_id.
Any violation raises `JoinIntegrityError` immediately.

### Layer C -- Reference Tables

| Reference | Module | Output Rows | Purpose |
|-----------|--------|-------------|---------|
| Zip Centroids | `src/geolocation.py` | 19,015 | Median lat/lng per 5-digit zip prefix (filtered to Brazilian bounds) |
| Category Translation | `src/category_translation.py` | 71 | Portuguese-to-English product category mapping |

### Layer D -- Canonical Order Base

The core join pipeline in `src/build_order_base.py` executes 6 validated joins:

| Step | Join | Key | Type | Match Rate |
|------|------|-----|------|-----------|
| D.1 | Orders + Customers | customer_id | Left 1:1 | 100.0% |
| D.2 | + Customer Centroids | customer_zip_code_prefix | Left M:1 | 99.7% |
| D.3 | + Aggregated Items | order_id | Left 1:1 | 99.2% |
| D.4 | + Dominant Seller + Centroids | dominant_seller | Left M:1 | 99.2% |
| D.5 | + Aggregated Payments | order_id | Left 1:1 | 100.0% |
| D.6 | + Selected Review | order_id | Left 1:1 | 99.2% |

**Validation:** After every join step, `JoinTracker` verifies:
- No row explosion (rows_after <= rows_before)
- Order grain preserved (1 row = 1 order_id)
- Telemetry recorded (source_table, join_type, match_rate, columns_added)

Layer D adds 3 population flags and 3 financial diagnostics:
- `is_delivered`, `has_delivery_date`, `eligible_for_delivery_analysis`
- `financial_diff`, `financial_abs_diff`, `financial_reconciled_flag`

### Layer E -- Missingness Flags

9 boolean flags that explicitly track data availability:

| Flag | Source Column | True Count | Null Pct |
|------|-------------|------------|----------|
| has_items | item_count | ~98,666 | 0.8% |
| has_payment_record | payment_value_total | ~99,440 | <0.01% |
| has_review | review_score | ~98,673 | 0.8% |
| has_customer_coordinates | customer_lat | ~99,162 | 0.3% |
| has_seller_coordinates | seller_lat | ~98,450 | 1.0% |
| has_product_category | dominant_category | ~98,666 | 0.8% |
| has_delivery_date | order_delivered_customer_date | ~96,476 | 3.0% |
| has_approval_date | order_approved_at | ~99,281 | 0.2% |
| has_carrier_date | order_delivered_carrier_date | ~97,658 | 1.8% |

**Design Rule:** Missing data is NEVER silently filled. Downstream analyses
must check the appropriate flag before using the corresponding data.

### Layer F -- Analytical Features

| Feature | Type | Logic |
|---------|------|-------|
| low_review_flag | bool | review_score <= 2 (where review exists) |
| high_review_flag | bool | review_score >= 4 (where review exists) |
| review_text_available | bool | review_comment_message is not null |
| review_title_available | bool | review_comment_title is not null |
| multi_item_order | bool | item_count > 1 |
| freight_share_pct | float | freight_total / order_gmv * 100 |
| discrepancy_bucket | str | Categorized financial diff (exact_match, minor, small, medium, large, no_data) |

### Layer G -- Temporal Features

| Feature | Type | Derivation |
|---------|------|-----------|
| purchase_year | Int64 | From order_purchase_timestamp |
| purchase_month | Int64 | From order_purchase_timestamp |
| purchase_year_month | str | Period string (e.g. 2017-01) |
| purchase_quarter | Int64 | From order_purchase_timestamp |
| purchase_day_of_week | Int64 | 0=Monday, 6=Sunday |
| purchase_day_name | str | Monday, Tuesday, etc. |
| purchase_hour | Int64 | Hour of day (0-23) |
| is_weekend_purchase | bool | Saturday or Sunday |
| delivery_days_total | float | Days from purchase to delivery |
| delivered_on_time | boolean | Actual <= estimated delivery |
| delivery_delay_days | float | Days beyond estimated (positive = late) |
| approval_to_carrier_days | float | Days from approval to carrier handoff |
| carrier_to_delivery_days | float | Days from carrier to customer delivery |

---

## 3. Financial Model

Two distinct financial concepts are tracked and **never forced to reconcile**:

| Concept | Definition | Column |
|---------|-----------|--------|
| **GMV** (Gross Merchandise Value) | sum(price + freight_value) at order grain | `order_gmv` |
| **Settlement Value** | sum(payment_value) at order grain | `payment_value_total` |

The difference (`financial_diff = GMV - Settlement`) is documented because
they represent different business concepts:
- GMV = merchant's commercial value of goods + shipping
- Settlement = cash actually tendered by the customer

---

## 4. Outputs

| File | Layer | Path |
|------|-------|------|
| Canonical Order Base (Parquet) | D | `data/processed/order_analytics_base.parquet` |
| Canonical Order Base (CSV) | D | `data/processed/order_analytics_base.csv` |
| Analytical Model (Parquet) | H | `data/processed/analytical_model.parquet` |
| Analytical Model (CSV) | H | `data/processed/analytical_model.csv` |
| Join Audit Telemetry | D | `outputs/tables/join_audit.csv` |
| Data Dictionary | H | `outputs/tables/order_analytics_data_dictionary.csv` |

---

## 5. Test Coverage

| Test File | Tests | Scope |
|-----------|-------|-------|
| `tests/test_data_contracts.py` | 29 | Raw sources, keys, aggregation contracts, base invariants |
| `tests/test_module2_data_model.py` | 65 | Grain, missingness, features, temporal, audit, dictionary, idempotency, financial, delivery |
| **Total** | **94** | **Full pipeline coverage** |

---

## 6. Reproducibility

Running the pipeline is idempotent:

```bash
python src/build_order_base.py
```

This command:
1. Reads from `data/raw/` (never modified)
2. Builds all aggregations from scratch
3. Executes validated joins
4. Applies feature engineering layers
5. Saves both Layer D and Layer H outputs
6. Emits join audit and data dictionary
7. All 94 tests pass on the resulting outputs
