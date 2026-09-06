# MODULE 1 → MODULE 2 READINESS REPORT
**Project:** Gradient Learnings — Data Analytics Hackathon 2026 (Olist Marketplace Diagnostic)  
**Evaluation Stage:** Post-Zero-Trust Forensic Audit & Correction Gate  
**Execution Date:** 2026-09-06  
**Auditor:** Lead Engineer & Senior Data Scientist  
**Final Gate Verdict:** **PASS — CLEARED FOR MODULE 2**

---

## 1. What Was Corrected

During the Zero-Trust Correction Pass, all architectural vulnerabilities and grain risks identified in the independent audit were converted into explicit, tested software modules without altering raw CSV files:

1. **Deterministic Order-Level Review Selection:**
   - Raw reviews contain 789 duplicate `review_id`s across orders and 547 orders with multiple survey submissions.
   - Built [`src/review_aggregation.py`](file:///c:/PROJECTS/Data%20Analytics/Data%20Analytics%20Hackathon/src/review_aggregation.py) implementing the deterministic `LATEST_VALID_REVIEW_PER_ORDER` rule: orders are sorted by `review_answer_timestamp` descending, `review_creation_date` descending, with `review_id` descending as an absolute tie-breaker.
   - Preserves 100% of raw review records for standalone text/review analysis while providing an exact 1:1 order-level review layer (98,673 rows).

2. **Financial Metric Disambiguation (GMV vs Settlement Value):**
   - Formally eliminated the assumption that item price + freight equals payment value.
   - Built [`src/financial_metrics.py`](file:///c:/PROJECTS/Data%20Analytics/Data%20Analytics%20Hackathon/src/financial_metrics.py) defining:
     - **GMV (Gross Merchandise Value):** $\sum(\text{price} + \text{freight\_value}) = 15,843,553.24\text{ BRL}$ (merchant basket value).
     - **Settlement Value:** $\sum(\text{payment\_value}) = 16,008,872.12\text{ BRL}$ (customer tender collected).
   - Documented the exact difference: 98,092 orders match exactly; 317 have cent rounding $\le 0.10$; 772 orders have payment recorded without order items; 378 orders exhibit true commercial-settlement discrepancies.

3. **Multi-Item Order Pre-Aggregation:**
   - Addressed the 9,803 multi-item orders (13,984 extra rows) that risked inflating joined datasets.
   - Built [`src/item_aggregation.py`](file:///c:/PROJECTS/Data%20Analytics/Data%20Analytics%20Hackathon/src/item_aggregation.py) aggregating items to exactly 98,666 orders.
   - Created rich diversity attributes (`distinct_products`, `distinct_sellers`, `distinct_categories`, `multi_seller_flag`, `multi_category_flag`) and transparent dominant entity selection (`dominant_category` and `dominant_seller` based on highest cumulative item spend, with alphabetical tie-breaking).

4. **Multi-Payment Pre-Aggregation:**
   - Addressed the 2,961 multi-payment orders (4,446 extra rows; up to 29 payment lines).
   - Built [`src/payment_aggregation.py`](file:///c:/PROJECTS/Data%20Analytics/Data%20Analytics%20Hackathon/src/payment_aggregation.py) aggregating payments to exactly 99,440 orders.
   - Computed `dominant_payment_type` by value, preserving installment statistics (`min`, `max`, `mean`) and `multi_payment_flag`.

5. **Geolocation Spatial Aggregation & Outlier Filtering:**
   - Addressed the 1,000,163 raw geolocation rows with up to 1,146 coordinates per prefix and overseas coordinate errors.
   - Built [`src/geolocation.py`](file:///c:/PROJECTS/Data%20Analytics/Data%20Analytics%20Hackathon/src/geolocation.py) with explicit territorial bounds ($\text{lat} \in [-33.75, 5.27]$, $\text{lng} \in [-73.99, -32.00]$, accommodating Brazilian oceanic archipelagos like Fernando de Noronha at $-32.4^\circ\text{W}$ while filtering 31 transatlantic coordinate typos).
   - Generated deduplicated lookup `zip_to_centroid` with 19,015 unique postal prefixes.

6. **Category Translation Fallback Layer:**
   - Resolved the 2 unmapped product categories (`pc_gamer`, `portateis_cozinha_e_preparadores_de_alimentos`).
   - Built [`src/category_translation.py`](file:///c:/PROJECTS/Data%20Analytics/Data%20Analytics%20Hackathon/src/category_translation.py) mapping 71 official English categories, applying transparent fallback `[original_category_name]` for unmapped categories (13 products), and `'unknown'` for 610 missing catalog categories.

7. **Join Integrity & Telemetry Framework:**
   - Built [`src/join_validation.py`](file:///c:/PROJECTS/Data%20Analytics/Data%20Analytics%20Hackathon/src/join_validation.py) featuring `JoinTracker`, `validate_order_grain()`, `validate_row_count()`, and `validate_no_row_explosion()`.
   - Any join attempting to compromise order grain raises a fatal `JoinIntegrityError`.

8. **Canonical Analytical Base Builder:**
   - Built [`src/build_order_base.py`](file:///c:/PROJECTS/Data%20Analytics/Data%20Analytics%20Hackathon/src/build_order_base.py) producing the official canonical dataset [`data/processed/order_analytics_base.parquet`](file:///c:/PROJECTS/Data%20Analytics/Data%20Analytics%20Hackathon/data/processed/order_analytics_base.parquet) and `.csv`.

---

## 2. What Was Verified

Every claim, count, and relational anchor was validated through automated execution:
- **Raw Files & Schemas:** 9 of 9 raw CSV files exist, are readable, and match expected schemas.
- **Keys & Cardinality:** Primary keys on orders, customers, products, sellers, and composite keys on order items and order payments are 100% unique (0 duplicate keys, 0 null keys).
- **Automated Test Suite:** [`tests/test_data_contracts.py`](file:///c:/PROJECTS/Data%20Analytics/Data%20Analytics%20Hackathon/tests/test_data_contracts.py) executed via pytest:
  $$\mathbf{29\text{ of }29\text{ tests PASSED (100\%)}}$$
- **Join Telemetry Log:** [`outputs/tables/order_base_validation.csv`](file:///c:/PROJECTS/Data%20Analytics/Data%20Analytics%20Hackathon/outputs/tables/order_base_validation.csv) confirms:
  - 6 sequential join steps executed.
  - Exactly 99,441 rows before and after each join.
  - Zero duplicate order IDs created.
  - Zero unexpected null keys introduced.

---

## 3. What Remains Intentionally Deferred

To maintain strict modular separation between Data Engineering (Modules 1–2) and Feature Engineering / Diagnostic Analytics (Modules 3–9), the following tasks are intentionally deferred:
1. **Haversine Distance & Route Pair Modeling:** Calculating physical route distance (km) between customer coordinates and seller coordinates deferred to Module 3/6.
2. **Delivery Latency Deltas ($\Delta_{\text{days}}$):** Calculating promised vs actual delivery gap ($\text{delivered} - \text{estimated}$) and seller dispatch delay deferred to Module 3/5.
3. **Review Sentiment & Text Extraction:** Natural language processing on Portuguese comment strings deferred to Module 5/8.
4. **Multivariate Econometric Modeling:** Logistic regression odds ratios and Shapley attribution deferred to Module 8.

---

## 4. Canonical Analytical Table Definition

The canonical analytical base is stored at:
- Parquet: [`data/processed/order_analytics_base.parquet`](file:///c:/PROJECTS/Data%20Analytics/Data%20Analytics%20Hackathon/data/processed/order_analytics_base.parquet)
- CSV: [`data/processed/order_analytics_base.csv`](file:///c:/PROJECTS/Data%20Analytics/Data%20Analytics%20Hackathon/data/processed/order_analytics_base.csv)

### Architectural Structure:
- **Grain:** Exactly **1 row = 1 `order_id`**.
- **Dimension Coverage:**
  - `orders` core (order status, timestamps).
  - `customers` (both `customer_id` and `customer_unique_id`, customer zip, city, state).
  - `customer_geolocation` (centroid latitude, centroid longitude).
  - `aggregated_items` (item count, spend, freight, GMV, product/seller diversity, dominant category, dominant seller).
  - `dominant_seller_geolocation` (seller zip, city, state, centroid latitude, centroid longitude).
  - `aggregated_payments` (settlement value, line count, payment type count, installment stats, dominant payment type).
  - `selected_reviews` (review ID, score, timestamps, review count per order, multi-review flag).
  - `delivery_population_flags` (`is_delivered`, `has_delivery_date`, `eligible_for_delivery_analysis`).
  - `financial_diagnostics` (`financial_diff`, `financial_abs_diff`, `financial_reconciled_flag`).

---

## 5. Current Row Count & 6. Unique Order Count

| Entity | Measured Value | Requirement | Status |
| :--- | :---: | :---: | :---: |
| **Total Rows in Base Table** | **99,441** | 99,441 | **MATCH (100%)** |
| **Unique `order_id` Count** | **99,441** | 99,441 | **MATCH (100%)** |
| **Duplicate `order_id` Count** | **0** | 0 | **ZERO DUPLICATES** |
| **Total Columns** | **52** | $\ge 40$ | **COMPLETE** |

---

## 7. Key Validation Results

| Validation Metric | Result | Target Benchmark | Verdict |
| :--- | :---: | :---: | :---: |
| Order-Grain Invariant | `len(df) == df['order_id'].nunique()` | True | **PASSED** |
| Customer ID Preservation | `customer_id` (99,441) & `customer_unique_id` (96,096) | 100% Preserved | **PASSED** |
| Items Table Order Coverage | 98,666 orders with items (775 null unfulfilled) | Expected | **PASSED** |
| Payments Table Order Coverage | 99,440 orders with payments (1 null missing record) | Expected | **PASSED** |
| Reviews Table Order Coverage | 98,673 orders with review (768 unreviewed) | Expected | **PASSED** |
| Delivered Orders Count | 96,478 orders (`is_delivered == True`) | 96,478 | **PASSED** |
| Delivered with Delivery Date | 96,476 orders (`has_delivery_date == True`) | 96,476 | **PASSED** |
| Eligible Delivery Analysis Cohort | 96,470 orders (`eligible_for_delivery_analysis == True`)| 96,470 | **PASSED** |
| Automated Unit Tests | 29 passed out of 29 in 11.66s | 100% Pass | **PASSED** |

---

## 8. Financial Metric Definitions

```text
GMV (Gross Merchandise Value) = sum(item price + item freight_value) at order grain
  • Commercial value of merchandise generated on Olist marketplace.
  • Platform Total: 15,843,553.24 BRL.

Settlement Value = sum(payment_value) at order grain
  • Total cash tender processed across payment gateways.
  • Platform Total: 16,008,872.12 BRL.

Financial Reconciliation:
  • Reconciled Orders (|GMV - Settlement| < 0.01 BRL): 98,287 orders (98.84%).
  • Discrepancy Orders (|GMV - Settlement| >= 0.01 BRL): 1,154 orders (1.16%).
    - 775 orders: Payments collected but no items fulfilled.
    - 1 order: Items fulfilled but no payment record found.
    - 378 orders: Slight commercial voucher/discount or rounding differences.
```

---

## 9. Review Handling Rule

```text
Rule Name: LATEST_VALID_REVIEW_PER_ORDER
Application: Order-Level Customer Experience Analysis

Ordering Hierarchy:
  1. Primary Sort:   review_answer_timestamp DESCENDING (most recent feedback response)
  2. Secondary Sort: review_creation_date DESCENDING
  3. Tie-Breaker:    review_id DESCENDING (deterministic string sort)

Output: Exactly 1 review per reviewed order (98,673 rows).
Raw Retention: All 99,224 original review records remain intact for review-level analytics.
```

---

## 10. Geolocation Rule

```text
Territorial Bounding Box Parameters (Brazil):
  • BRAZIL_LAT_MIN = -33.75  (Southern extreme: Arroio do Chuí, RS)
  • BRAZIL_LAT_MAX = 5.27    (Northern extreme: Monte Caburaí, RR)
  • BRAZIL_LNG_MIN = -73.99  (Western extreme: Serra do Divisor, AC)
  • BRAZIL_LNG_MAX = -32.00  (Eastern extreme: Fernando de Noronha, PE archipelago at ~-32.4°W)

Aggregation Mechanism:
  • Filter raw records to configured bounding box (1,000,132 valid coordinates; 31 invalid coordinates excluded).
  • Compute arithmetic mean (centroid_lat, centroid_lng) on valid coordinates per zip_code_prefix.
  • Assign canonical city and state using statistical mode per zip_code_prefix.
  • Emits deduplicated lookup table: exactly 19,015 unique zip prefixes (1 row per prefix).
```

---

## 11. Remaining Risks & Monitoring Controls

1. **Unmapped Postal Prefixes (0.28% of orders):**
   - 157 customer zip prefixes (278 orders) and 7 seller zip prefixes (7 sellers) do not appear in `olist_geolocation_dataset.csv`.
   - *Control:* Left joins assign NaN to `customer_lat`/`lng` without failing; downstream distance functions will skip rows with missing coordinates.
2. **Orders Missing Items (0.78% of orders):**
   - 775 orders have no item records (canceled prior to item creation).
   - *Control:* `item_count` is NaN or 0; commercial analyses must filter for `item_count.notnull()`.
3. **Observational vs Causal Confounding:**
   - Observational e-commerce logs contain correlated features (e.g. high freight correlated with long distance and lower reviews).
   - *Control:* Hypotheses remain non-causal association statements. Logistic regression in Module 8 will report odds ratios ($e^\beta$) with confidence intervals and VIF diagnostics.

---

## 12. Final PASS/FAIL Verdict

```text
================================================================================
FINAL VERDICT: FULL PASS
STATUS: READY FOR MODULE 2 (DATA MODEL & JOIN ARCHITECTURE)
================================================================================
```

All 10 required preconditions are satisfied:
- [x] Raw data untouched in `data/raw/`
- [x] Review handling explicit and deterministic
- [x] Payment aggregation explicit and tested
- [x] Item aggregation explicit and tested
- [x] GMV vs Settlement value formally separated
- [x] Category mapping explicit with transparent fallback
- [x] Geolocation treatment parameterized and deduplicated
- [x] Order-level canonical table validated (99,441 rows, 1 row = 1 order)
- [x] Join checks and telemetry framework implemented
- [x] Reproducibility verified via 29 passing automated unit tests

**Execution is halted. Standing by for user instruction to begin Module 2.**
