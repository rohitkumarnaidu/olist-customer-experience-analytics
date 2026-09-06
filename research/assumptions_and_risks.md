# Assumptions, Constraints & Risk Mitigation Register
**Project:** Gradient Learnings — Data Analytics Hackathon 2026

---

## 1. Technical & Methodological Assumptions

1. **Analytical Anchor Grain:**
   * **Assumption:** The primary unit of customer experience and commercial transaction is the **Order** (`order_id`).
   * **Rule:** All item-level, payment-level, and review-level attributes must be deterministically aggregated to the `order_id` grain before conducting order-level statistical evaluations.

2. **Customer Identity:**
   * **Assumption:** `customer_id` is an order-scoped token, while `customer_unique_id` represents an actual human customer.
   * **Rule:** Repeat purchase rates and customer lifetime metrics must strictly use `customer_unique_id`.

3. **Delivery Validity:**
   * **Assumption:** Only orders with status `'delivered'` and non-null `order_delivered_customer_date` reflect realized delivery experiences.
   * **Rule:** Orders that were canceled, unavailable, or missing delivery timestamps must be isolated and analyzed separately under fulfillment failure audits, not mixed into delivery duration statistics.

4. **Geolocation Approximation:**
   * **Assumption:** `geolocation_zip_code_prefix` is non-unique (contains multiple coordinate records).
   * **Rule:** Coordinates must be collapsed to centroid/mean $(\bar{\text{lat}}, \bar{\text{lng}})$ per 5-digit prefix. Any coordinates falling outside standard Brazilian geographical bounds ($\text{lat} \in [-34, 6], \text{lng} \in [-74, -34]$) must be sanitized.

5. **Financial Accounting Integrity:**
   * **Assumption:** Total order value consists of item prices and freight values.
   * **Rule:** When joining `order_items` and `order_payments`, cross-table Cartesian multiplication must be strictly prevented.

---

## 2. Risk Mitigation Matrix

| Risk Factor | Impact | Likelihood | Mitigation Strategy |
| :--- | :---: | :---: | :--- |
| **Row Explosion in Joins** | Critical | High | Implement pre-join and post-join validation checks tracking `rows_before`, `rows_after`, and distinct `order_id` counts. |
| **Causal Overclaiming** | High | High | Explicitly treat regression coefficients as controlled associative risk multipliers rather than causal proofs. |
| **Small-Sample Corridor Distortion** | Medium | High | Enforce minimum sample thresholds ($N \ge 30$) before ranking seller cohorts or interstate corridors. |
| **Colab Environment Portability** | High | Medium | Avoid any hardcoded local paths; design relative paths and parameter configurations reproducible in Google Colab. |
| **Computational Overhead** | Medium | Medium | Vectorize all feature engineering logic; save clean intermediate datasets in Parquet format. |
