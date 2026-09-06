# Skills, Tools, and Analytical Architecture Plan
**Project:** Gradient Learnings — Data Analytics Hackathon 2026 (Olist Brazilian E-Commerce)  
**Roles:** Lead Engineer | Senior Data Scientist | Analytics Consultant | Data Visualization Expert | Hackathon Strategist

---

## 1. Skills Mapping & Deployment Strategy

To build a competition-winning, reproducible, and mathematically sound analytics project, we mobilize our specialized skills across every layer of the architecture:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SKILL & METHODOLOGY ARCHITECTURE                        │
├──────────────────────────┬───────────────────────────┬──────────────────────┤
│ Skill / Domain           │ Primary Modules           │ Technical Role       │
├──────────────────────────┼───────────────────────────┼──────────────────────┤
│ ferroxlabs-etl-architect │ Module 1, 2, 3            │ Strict grain audits, │
│                          │                           │ zero row explosion,  │
│                          │                           │ CDC/SCD mapping      │
├──────────────────────────┼───────────────────────────┼──────────────────────┤
│ ferroxlabs-data-pipeline │ Module 2, 4, 5            │ Order-level pipeline,│
│                          │                           │ clean idempotency,   │
│                          │                           │ feature engineering  │
├──────────────────────────┼───────────────────────────┼──────────────────────┤
│ brycewang-stanford-      │ Module 4, 7, 8, 9, 13,    │ Nonparametric tests, │
│ statistics               │ 14, 17, 18                │ power thresholds,    │
│                          │                           │ anomaly detection,   │
│                          │                           │ statistical validity │
├──────────────────────────┼───────────────────────────┼──────────────────────┤
│ affaan-m-mle-workflow    │ Module 5, 17, 18, 19, 20  │ Data contracts,      │
│                          │                           │ multivariate model,  │
│                          │                           │ odds ratios & VIF    │
├──────────────────────────┼───────────────────────────┼──────────────────────┤
│ leoyeai-senior-data-     │ Module 2, 3, 5, 27        │ Vectorized execution,│
│ engineer                 │                           │ intermediate caching,│
│                          │                           │ modular architecture │
├──────────────────────────┼───────────────────────────┼──────────────────────┤
│ Built-in ml-best-        │ Module 6-15, 21, 22, 23   │ Evidence hierarchy,  │
│ practices & visualization│                           │ business exposure,   │
│                          │                           │ executive charts     │
└──────────────────────────┴───────────────────────────┴──────────────────────┘
```

---

## 2. Granular Skill Applications by Project Phase

### Phase I: Ingestion, Grain Modeling & Audit (Modules 1 - 3)
*   **Skill: `ferroxlabs-etl-architect` & `ferroxlabs-data-pipeline`**
    *   *Core Anchor:* Enforce `order_id` as the atomic analytical grain.
    *   *De-duplication & Pre-aggregation:* Pre-aggregate items (order value, item count, freight sum, product category mapping), payments (total installments, dominant payment type, total payment value), reviews (handling orders with multiple reviews, latest review timestamp).
    *   *Geolocation Clustering:* Avoid Cartesian joins by computing mean coordinates $(\bar{\text{lat}}, \bar{\text{lng}})$ per `geolocation_zip_code_prefix` and filtering out coordinates outside Brazil bounding boxes.
    *   *Validation Gate:* Track and log `rows_before`, `rows_after`, `unique_orders_before`, `unique_orders_after`, and `null_keys` at every transformation.

### Phase II: Feature Engineering & Unified KPI Layer (Modules 4 - 5)
*   **Skill: `leoyeai-senior-data-engineer` & `affaan-m-mle-workflow`**
    *   *Vectorized Metrics:* 
        *   `delivery_duration_days = (order_delivered_customer_date - order_purchase_timestamp).dt.total_seconds() / 86400`
        *   `delay_days = (order_delivered_customer_date - order_estimated_delivery_date).dt.total_seconds() / 86400`
        *   `delay_bucket`: `Early (< 0)`, `On-Time (== 0)`, `1-3 Days Late`, `4-7 Days Late`, `> 7 Days Late (Severe)`
        *   `freight_ratio = freight_value / (price + 1e-6)`
        *   `haversine_distance_km = f(customer_lat, customer_lng, seller_lat, seller_lng)`
    *   *Data Contracts:* Strict type checking and value range assertions.

### Phase III: Multi-Perspective Marketplace Analytics (Modules 6 - 15)
*   **Skill: `brycewang-stanford-statistics`**
    *   *Nonparametric Tests:* Because `review_score` is ordinal (1 to 5) and heavily non-normal, use **Mann-Whitney $U$** and **Kruskal-Wallis** tests for comparing satisfaction across delay buckets, regions, and categories.
    *   *Power & Minimum Sample Size:* Establish minimum order thresholds (e.g., $N \ge 30$ or $N \ge 50$) for seller cohorts and state-to-state corridors ($S_{\text{state}} \times C_{\text{state}}$) to prevent small-sample noise.
    *   *Haversine Spatial Corridors:* Compute route efficiency and freight equity across interstate corridors.

### Phase IV: Root Cause Modeling & Validation (Modules 17 - 18)
*   **Skill: `affaan-m-mle-workflow` & `brycewang-stanford-statistics`**
    *   *Target:* Binary outcome `low_review = 1` if `review_score <= 2`, else `0`.
    *   *Model:* Multivariate Logistic Regression (Statsmodels / Scikit-Learn).
    *   *Interpretability:* Compute Odds Ratios ($e^\beta$) with 95% Confidence Intervals and $p$-values.
    *   *Diagnostics:* Variance Inflation Factor (VIF) to detect multicollinearity, Hosmer-Lemeshow calibration check, ROC-AUC score.
    *   *Strict Guardrail:* Do NOT claim observational coefficients are causal mechanisms; report them as controlled associative risk multipliers.

### Phase V: High-Impact Segmentation, Exposure & Recommendations (Modules 19 - 25)
*   **Skill: `ml-best-practices` & Strategic Consulting Framework**
    *   *Interactive Segmentation Tree:* Discover empirical intersections (e.g., `Severe Delay` $\times$ `Specific Corridors` $\times$ `Bulky Categories`).
    *   *Business Exposure Metric:*
        $$\text{Exposure} = \frac{\text{Segment Low Reviews}}{\text{Platform Total Low Reviews}} \times 100\%$$
    *   *Prioritization Triage:*
        *   **P0 (Must Fix):** High dissatisfaction share + High revenue at risk + Direct operational lever.
        *   **P1 (High Priority):** Moderate volume + Severe SLA violation.
        *   **P2 (Strategic/Long-term):** Structural/infrastructure carrier contracts.
    *   *Standardized Recommendation Schema:* **Problem $\rightarrow$ Segment $\rightarrow$ Evidence $\rightarrow$ Mechanism $\rightarrow$ Intervention $\rightarrow$ Impact $\rightarrow$ KPI**.

### Phase VI: Competition Colab Assembly & Presentation (Modules 26 - 27)
*   **Skill: `leoyeai-senior-data-engineer` & Visualization Guidelines**
    *   Produce a single self-contained, beautifully rendered Google Colab notebook (`Olist_Final_Analysis.ipynb`) that runs top-to-bottom without manual intervention.
