# Module 2 Completion Report -- Data Model and Join Architecture

**Project:** Gradient Learnings Data Analytics Hackathon 2026 (Olist)
**Module:** 2 -- Data Model and Join Architecture
**Status:** COMPLETED
**Date:** 2026-09-06

---

## 1. Objective

Build a trusted, reusable analytical model preserving the invariant
**1 row = 1 order_id** throughout all downstream analysis, with layered
feature engineering and comprehensive validation.

## 2. Deliverables

| Deliverable | Status | Path |
|------------|--------|------|
| `data_loader.py` | COMPLETE | `src/data_loader.py` |
| `data_model.py` | COMPLETE | `src/data_model.py` |
| `build_order_base.py` (enhanced) | COMPLETE | `src/build_order_base.py` |
| `join_validation.py` (enhanced) | COMPLETE | `src/join_validation.py` |
| Canonical Order Base (Parquet) | COMPLETE | `data/processed/order_analytics_base.parquet` |
| Canonical Order Base (CSV) | COMPLETE | `data/processed/order_analytics_base.csv` |
| Analytical Model (Parquet) | COMPLETE | `data/processed/analytical_model.parquet` |
| Analytical Model (CSV) | COMPLETE | `data/processed/analytical_model.csv` |
| Join Audit Telemetry | COMPLETE | `outputs/tables/join_audit.csv` |
| Data Dictionary | COMPLETE | `outputs/tables/order_analytics_data_dictionary.csv` |
| Architecture Documentation | COMPLETE | `research/analytical_data_model.md` |
| Extended Test Suite | COMPLETE | `tests/test_module2_data_model.py` |

## 3. Model Dimensions

| Layer | Rows | Columns | Description |
|-------|------|---------|-------------|
| Layer D (Canonical Base) | 99,441 | 52 | Validated joins + population flags + financial diagnostics |
| Layer H (Analytical Model) | 99,441 | 80 | Full model with missingness, features, temporal dims |

## 4. Join Pipeline Results

All 6 join steps passed validation with zero row explosion:

| Step | Right Table | Key | Match Rate |
|------|-------------|-----|-----------|
| D.1 | Customers | customer_id | 100.0% |
| D.2 | Zip Centroids (Customer) | customer_zip_code_prefix | 99.7% |
| D.3 | Items Aggregated | order_id | 99.2% |
| D.4 | Sellers + Centroids | dominant_seller | 99.2% |
| D.5 | Payments Aggregated | order_id | 100.0% |
| D.6 | Reviews Selected | order_id | 99.2% |

## 5. Key Population Statistics

### Delivery Analysis Population
- Orders with status=delivered: 96,478 (97.0%)
- Orders with delivery date: 96,476
- Orders eligible for delivery analysis: 96,470

### Review Coverage
- Orders with reviews: 98,673 (99.2%)
- Low reviews (score <= 2): 14,494 (14.6%)
- High reviews (score >= 4): 76,046 (76.5%)

### Financial Reconciliation
- Exactly reconciled (|diff| < 0.01 BRL): 98,287 (98.8%)
- Mean absolute difference: 1.67 BRL
- Discrepancy distribution:
  - exact_match: 98,287
  - minor (<1 BRL): 131
  - small (<10 BRL): 151
  - medium (<100 BRL): 454
  - large (>=100 BRL): 418

### Temporal Coverage
- Date range: 2016 -- 2018
- Unique year-months: 25 periods

## 6. Test Results

| Test Suite | Tests | Result |
|-----------|-------|--------|
| `tests/test_data_contracts.py` | 29 | 29 PASSED |
| `tests/test_module2_data_model.py` | 65 | 65 PASSED |
| **Total** | **94** | **94 PASSED** |

Test coverage includes:
- Raw source file presence and row counts (9 files)
- Column schema validation (9 schemas)
- Primary/composite key uniqueness (6 tables)
- Aggregation contract enforcement (3 aggregations)
- Order grain invariant (both Layer D and Layer H)
- Missingness flag consistency (9 pairs)
- Analytical feature correctness (6 features)
- Temporal feature ranges (7 dimensions)
- Join audit completeness (4 checks)
- Data dictionary coverage (3 checks)
- Idempotency between Parquet and CSV (2 checks)
- Financial integrity (3 checks)
- Delivery population flags (2 checks)

## 7. Feature Engineering Summary

### Layer E -- Missingness Flags (9 columns added)
Explicit boolean indicators for data availability. No silent null filling.

### Layer F -- Analytical Features (8 columns added)
- `low_review_flag`, `high_review_flag` -- review score brackets
- `review_text_available`, `review_title_available` -- text presence
- `multi_item_order` -- boolean for multi-item orders
- `freight_share_pct` -- freight as % of GMV
- `discrepancy_bucket` -- financial diff categorization

### Layer G -- Temporal Features (13 columns added)
- Purchase date dimensions: year, month, quarter, day, hour
- Weekend flag
- Delivery performance: total days, on-time flag, delay days
- Pipeline stages: approval-to-carrier, carrier-to-delivery

## 8. Readiness for Module 3

The analytical model is ready for downstream analysis:

1. **All downstream modules should load from:**
   - `data/processed/analytical_model.parquet` (Layer H -- full features)
   - OR `data/processed/order_analytics_base.parquet` (Layer D -- base only)

2. **Data loader available:** `from src.data_loader import load_canonical_base`

3. **Grain guarantee:** 99,441 rows = 99,441 unique order_ids

4. **Missingness is explicit:** Check `has_*` flags before analysis

5. **Financial concepts are separated:** GMV != Settlement Value (by design)

6. **Temporal dimensions are pre-computed:** No date parsing needed downstream

---

**MODULE 2: COMPLETE**
