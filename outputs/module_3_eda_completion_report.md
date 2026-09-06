# Module 3 Completion Report — Exploratory Data Analysis (EDA)

**Project:** Gradient Learnings Data Analytics Hackathon 2026 (Olist)  
**Module:** 3 — Exploratory Data Analysis (EDA)  
**Status:** COMPLETED  
**Date:** 2026-09-06  
**Analytical Grain:** 1 row = 1 `order_id` (99,441 rows strictly preserved)  
**Automated Test Status:** **130 of 130 Tests PASSED (100%)**

---

## 1. Module Objective

To conduct an exhaustive, evidence-driven, business-question-led Exploratory Data Analysis (EDA) across the Olist Brazilian e-commerce ecosystem. The analysis establishes baseline KPIs, maps marketplace concentration, evaluates growth-quality divergence over time, dissects delivery and review dynamics, uncovers critical operational mechanisms (notably the CRM survey trigger defect), tests initial hypotheses, and generates a prioritized finding register to guide downstream modeling.

---

## 2. Dataset Utilized

- **Primary Analytical Base:** `data/processed/analytical_model.parquet` (Layer H, 99,441 rows × 80 columns).
- **Secondary Validated Relational Tables:** `olist_orders_dataset.csv`, `olist_order_items_dataset.csv`, `olist_order_payments_dataset.csv`, `olist_order_reviews_dataset.csv`, `olist_customers_dataset.csv`, `olist_sellers_dataset.csv`, `olist_products_dataset.csv`, `olist_geolocation_dataset.csv`, and `product_category_name_translation.csv`.
- **Integrity Guarantee:** Zero row multiplication across 6 join steps; 100% primary and composite key uniqueness verified.

---

## 3. Executive KPI Baseline

Validated against official problem statement specifications and saved at [`outputs/tables/eda_kpi_baseline.csv`](file:///c:/PROJECTS/Data%20Analytics/Data%20Analytics%20Hackathon/outputs/tables/eda_kpi_baseline.csv):

| KPI Name | Value | Unit | Grain | Target Population | Status |
| :--- | :---: | :---: | :---: | :--- | :---: |
| **Total Orders** | 99,441 | Orders | Platform | All Transactions | **VERIFIED** |
| **Delivered Orders** | 96,478 | Orders | Platform | `order_status == 'delivered'` | **VERIFIED** |
| **Non-Delivered Orders** | 2,963 | Orders | Platform | Canceled, shipped, unavailable | **VERIFIED** |
| **Delivered Rate** | 97.02% | Percentage | Platform | All Transactions | **VERIFIED** |
| **Total GMV (Price + Freight)** | R$ 15,843,553.24 | BRL | Platform | Orders with Items (98,666) | **VERIFIED** |
| **Total Settlement Value** | R$ 16,008,872.12 | BRL | Platform | Orders with Payments (99,440) | **VERIFIED** |
| **Average Order Value (AOV)** | R$ 160.58 | BRL / Order | Order | Orders with Items | **VERIFIED** |
| **Average Review Score** | 4.09 | Stars (1–5) | Order | Orders with Review (98,673) | **VERIFIED** |
| **1-Star Review Rate** | 11.52% | Percentage | Order | Orders with Review | **VERIFIED** |
| **1–2 Star (Low Review) Rate** | 14.69% | Percentage | Order | Orders with Review | **VERIFIED** |
| **4–5 Star (High Review) Rate** | 77.07% | Percentage | Order | Orders with Review | **VERIFIED** |
| **Late Delivery Rate** | 8.11% | Percentage | Order | Eligible Delivered (96,470) | **VERIFIED** |
| **Severe Delay Rate (>7d Late)** | 3.46% | Percentage | Order | Eligible Delivered (96,470) | **VERIFIED** |
| **Average Delivery Duration** | 12.6 | Days | Order | Eligible Delivered | **VERIFIED** |
| **Median Delivery Duration** | 10.2 | Days | Order | Eligible Delivered | **VERIFIED** |
| **Average Freight Value** | R$ 22.82 | BRL / Order | Order | Orders with Items | **VERIFIED** |
| **Median Freight Value** | R$ 17.17 | BRL / Order | Order | Orders with Items | **VERIFIED** |
| **Repeat Customer Rate** | 3.12% | Percentage | Customer | Unique Customers (96,096) | **VERIFIED** |
| **Repeat Order Volume Share** | 6.38% | Percentage | Order | All Orders (99,441) | **VERIFIED** |

---

## 4. Major EDA Observations

1. **Marketplace Structure:**
   - 90.7% of transactions are single-item orders; 98.8% involve a single seller.
   - Severe seller revenue concentration: the **top 10% of sellers generate 66.7% of total platform GMV** and 62.2% of orders.
   - Category concentration: Top 10 categories account for 63.0% of orders and 58.4% of GMV (Category HHI: 484.2).
2. **Time & Growth Divergence:**
   - Order volume expanded over **8x** from Jan 2017 (800 orders) to Aug 2018 (6,512 orders).
   - No chronic secular decline in review scores was observed; the platform maintained a stable baseline around 4.10–4.20 stars.
   - Growth-quality divergence occurred acutely during **Black Friday (Nov 2017)**: order volume spiked 63% MoM (7,544 orders), postal bottlenecks pushed late rate to 16.2%, and satisfaction temporarily dipped to 3.82 stars before recovering within 90 days.
3. **Delivery Heuristics & Expectation Buffers:**
   - **92.9% of delivered orders arrive early**. The median package arrives **11.95 days ahead of the promised delivery date**.
   - Because delivery estimates are so padded, by the time an order is "late," the customer has already waited over 25 days on average.
4. **Customer Retention:**
   - Only 3.12% of unique buyers (2,997) made repeat purchases, generating 6.38% of total orders. Olist operates primarily as a customer acquisition marketplace.
5. **Financing Mechanics:**
   - Credit cards fund 75.4% of orders and 78.4% of GMV.
   - 75.4% of credit card transactions use installment financing, scaling monotonically with ticket size (from R$ 98.7 for 1 installment to R$ 421.3 for 10 installments).
6. **Geographic Hegemony:**
   - **São Paulo state (SP)** supplies **70.3% of all seller shipments** and generates 41.8% of platform demand. Outbound corridors from SP into the Northeast (BA, CE, PE) and North (AM, PA) suffer delay rates exceeding 11% to 18%.

---

## 5. Important Multi-Variable Interactions

Documented in [`outputs/tables/eda_interaction_candidates.csv`](file:///c:/PROJECTS/Data%20Analytics/Data%20Analytics%20Hackathon/outputs/tables/eda_interaction_candidates.csv):

1. **Delivery Delay Severity $\times$ Review Score (Strong, Spearman $\rho = -0.334$):**
   - Non-linear collapse: On-time (4.29 stars) $\to$ 1–3d late (3.76 stars) $\to$ 4–7d late (2.32 stars) $\to$ >7d late (1.73 stars, 76.3% low reviews).
2. **Survey Timing (In-Transit vs Post-Delivery) $\times$ Low Review Rate (Extremely Strong, Odds Ratio: 7.64):**
   - When survey is sent after delivery: 4.28 stars (9.4% low reviews).
   - When survey is prompted while package is still in transit: 1.98 stars (70.9% low reviews).
3. **Haversine Distance $\times$ Delivery Duration (Moderate-Strong, Spearman $\rho = +0.401$):**
   - Physical distance adds 8 to 15 days of transit for inter-regional routes (>2,000 km).
4. **Freight Share % $\times$ Review Score (Weak, Spearman $\rho = -0.065$):**
   - Dissatisfaction is driven by transit lateness, not shipping fees. Customers tolerate high freight fees for distant orders as long as promised dates are kept.
5. **Product Category $\times$ Delay Sensitivity (Interaction $F = 4.82, p < 0.0001$):**
   - Bulky furniture tolerates minor delays with smaller rating penalties (-0.8 stars) compared to electronics and personal care (-1.4 stars).

---

## 6. Anomaly & Outlier Classification

Documented in [`outputs/tables/eda_anomaly_register.csv`](file:///c:/PROJECTS/Data%20Analytics/Data%20Analytics%20Hackathon/outputs/tables/eda_anomaly_register.csv):

- **ANOM-01 (Extreme Duration >60d):** 306 orders (max 209.6d) $\to$ *Legitimate Operational Extreme* (remote Amazon transit, lost shipments).
- **ANOM-02 (Severe Delay >30d late):** 360 orders (max 189.0d late) $\to$ *Legitimate Operational Extreme* (carrier failure, stockouts; 92% receive 1-star).
- **ANOM-03 (Carrier logged prior to approval):** 1,359 orders $\to$ *Data Logging Artifact* (offline boleto processing, manual batch scans, timezone drift).
- **ANOM-04 (Delivered logged prior to carrier):** 23 orders $\to$ *Data Entry / Scanning Error* (carrier skipped origin scan, scanned only on delivery).
- **ANOM-05 (GMV vs Settlement diff > R$ 100):** 417 orders $\to$ *Legitimate Voucher / Multi-Tender Anomaly* (promotional marketplace credits).
- **ANOM-06 (Catalog weight = 0.0g):** 4 products (`cama_mesa_banho`) $\to$ *Catalog Ingestion Omission*.

---

## 7. Supported Hypotheses

- **H2 (Non-linear dissatisfaction drop):** Supported. Catastrophic rating cliff beyond 7 days late.
- **H3 (Conservative delivery estimates):** Supported. 92.9% delivered early; median is 11.95 days early.
- **H4 (Inter-regional delay penalty):** Supported. Interstate long-haul routes exhibit 3x higher failure rates.
- **H5 (High freight $\ne$ speed):** Supported. Highest freight quintile takes 17.8d vs 10.4d for lowest.
- **H7 (Delay is primary driver):** Supported. Spearman $\rho = -0.334$ dwarfs price and installments ($\rho < 0.05$).
- **H8 (Concentration of negative reviews):** Supported. 5.4% in-transit surveyed orders drive 26.1% of all negative reviews.

---

## 8. Contradicted / Weakened Hypotheses

- **H1 (Platform growth degrades satisfaction over time):** **Partially Supported / Weakened**. Average review scores remained resilient around 4.10–4.20 stars across 2017 and 2018. Degradation was an acute capacity shock during Black Friday 2017, not chronic platform decay.
- **H6 (Bulky categories delay tolerance):** **Partially Supported / Weakened**. Tolerance exists for minor delays (1–3 days), but collapses for severe delays (>7 days late) where all categories suffer >75% negative reviews.

---

## 9. Differentiating Findings

1. **The 12-Day Expectation Buffer:** Explaining that because 92.9% of packages arrive early, when an order breaches the promised estimate, customer patience has already expired.
2. **Category Delay Tolerance Heterogeneity:** Demonstrating that delivery promises should be category-differentiated rather than uniform.
3. **Decoupling Freight from Dissatisfaction:** Proving that customers do not punish Olist for high shipping fees, but rather for unpredictable transit times.

---

## 10. Signature Insight Candidate

### **The CRM Premature Survey Trigger Defect (FIND-01)**
- **Finding:** 8,140 reviews were created before the order was recorded as delivered. Specifically, when an order is delayed past its estimated delivery date, Olist's automated system sends the satisfaction survey while the package is still in transit (5,335 orders).
- **Impact:** Customers rate the premature survey with **1.98 stars average (70.9% 1–2 star rate)**.
- **Scale:** Accounts for **3,782 low reviews — over 26% of all negative reviews on the platform**.
- **Actionability:** An immediate, zero-capex operational software fix (suppressing surveys until carrier delivery confirmation or sending a proactive delay notice) will eliminate up to 26% of low review volume.

---

## 11. Questions Requiring Formal Statistical Testing

1. **Multivariate Econometric Isolation (Module 17):**
   - Run logistic regression with Odds Ratios ($e^\beta$) and VIF diagnostics to verify that delay severity remains dominant after controlling for category, price, freight, seller, and state.
2. **Threshold Inflection Estimation (Module 7/17):**
   - Fit piecewise linear models to pinpoint the exact inflection day where review scores collapse.
3. **Corridor Fixed Effects (Module 9/10):**
   - Disentangle carrier routing inefficiencies from raw geographical distance.

---

## 12. Recommended Next Modules

1. **Module 4 — Trusted KPI Layer:** Codify validated metrics into `src/kpis.py`.
2. **Module 5 — Feature Engineering:** Create delay severity buckets, corridor pairs, and survey trigger flags.
3. **Modules 6–15 — Core Questions & Multi-Angle Analytics:** Deep-dive econometric modeling on time series, delivery, corridors, and category economics.
4. **Modules 17–18 — Root Cause Multivariate Modeling:** Formal logistic regression and decision-tree segmentation.
5. **Modules 19–23 — Strategic Prioritization & P0/P1/P2 Roadmap:** Quantify business exposure and ROI.

---

## 13. Visualization Inventory (18 Core Visuals)

All 18 publication-grade visualization artifacts generated at 300 DPI in `outputs/figures/`:

1. `fig01_monthly_marketplace_growth_divergence.png` (377 KB) — Monthly Growth vs. Customer Sentiment & Delivery SLA
2. `fig02_order_status_composition.png` (192 KB) — Order Completion vs In-Transit/Cancellation Breakdown
3. `fig03_seller_concentration_pareto.png` (228 KB) — Seller Revenue Concentration Pareto / Lorenz Curve
4. `fig04_category_volume_vs_revenue_share.png` (154 KB) — Top 10 Product Categories Volume vs. Revenue Share
5. `fig05_delivery_duration_distribution.png` (189 KB) — Elapsed Purchase-to-Delivery Duration Distribution
6. `fig06_delivery_delay_distribution_and_buffer.png` (133 KB) — Promised vs. Actual Delivery Gap (The 12-Day Buffer)
7. `fig07_review_score_distribution_polarization.png` (134 KB) — Review Score J-Curve Polarization
8. `fig08_review_score_by_delay_bucket.png` (226 KB) — Review Score Collapse Across Delay Severity Buckets
9. `fig09_survey_trigger_pre_vs_post_delivery.png` (179 KB) — Rating Collapse for Overdue In-Transit Surveys
10. `fig10_payment_type_share_and_aov.png` (178 KB) — Payment Method Volume Share vs. Average Order Value
11. `fig11_installments_vs_ticket_value.png` (232 KB) — Financing Depth: Order Basket Size vs. Installments
12. `fig12_geographic_flow_seller_to_customer_states.png` (161 KB) — State Fulfillment Dependency on São Paulo
13. `fig13_haversine_distance_vs_delivery_duration.png` (791 KB) — Great-Circle Distance vs. Delivery Duration
14. `fig14_regional_corridor_delay_heatmap.png` (232 KB) — Top High-Volume Interstate Logistics Arteries by Delay Rate
15. `fig15_category_delay_vs_review_sensitivity.png` (226 KB) — Category Delivery Vulnerability vs. Review Score
16. `fig16_freight_share_vs_satisfaction.png` (137 KB) — Shipping Cost Share vs. Customer Sentiment
17. `fig17_repeat_vs_onetime_customer_experience.png` (119 KB) — Retention Contrast: One-Time vs. Repeat Experience
18. `fig18_executive_exploratory_dashboard.png` (468 KB) — 6-Panel Executive Exploratory Dashboard

---

## 14. QA Status

- **Automated Verification:** **130 of 130 tests PASSED (100%)**
  - `tests/test_data_contracts.py`: 29 / 29 PASSED
  - `tests/test_module2_data_model.py`: 65 / 65 PASSED
  - `tests/test_module3_eda.py`: 36 / 36 PASSED
- **Executable Notebook:** `notebooks/03_exploratory_data_analysis.ipynb` (42 cells, executes cleanly with zero errors).
- **All 11 CSV Output Tables Present & Populated.**

---

**MODULE 3 (EXPLORATORY DATA ANALYSIS): COMPLETED**
