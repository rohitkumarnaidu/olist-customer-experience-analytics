# Exploratory Data Analysis (EDA) Executive Summary

**Project:** Gradient Learnings Data Analytics Hackathon 2026 (Olist)  
**Module:** 3 — Exploratory Data Analysis  
**Primary Dataset:** `data/processed/analytical_model.parquet` (99,441 rows × 80 columns)  
**Author:** Lead Analytics Consultant & Data Scientist  
**Date:** 2026-09-06  

---

## 1. What Do We Now Know?

1. **Commercial Scale & Composition:**
   - Over the 25-month observation window (September 2016 – October 2018), the marketplace transacted **99,441 orders** representing **R$ 15,843,553.24 in Gross Merchandise Value (GMV)** and **R$ 16,008,872.12 in Settlement Value**.
   - The platform is overwhelmingly a **single-item marketplace**: 90.7% of orders contain exactly 1 item, and 98.8% involve a single seller.
   - **97.02% of orders (96,478)** achieved successful delivery status, with 2,963 orders stalling across transit, cancellation, or unavailability.

2. **Customer Sentiment Profile:**
   - Sentiment is heavily polarized into a **J-curve**: 57.8% of reviews are 5-star, 19.3% are 4-star, while 11.5% are 1-star and 3.1% are 2-star. Mid-tier ratings (3-star) represent only 8.2%.
   - Platform-wide average review score is **4.09 out of 5.00**.

3. **Logistics Performance & Fulfillment Reality:**
   - Median delivery duration from purchase to customer delivery is **10.2 days** (mean 12.6 days).
   - **92.9% of delivered orders arrive on or before the estimated delivery date**. Median arrival is **11.95 days earlier than promised**, demonstrating a systematically conservative heuristics buffer.
   - However, **8.11% of eligible orders (7,827)** breach the promised delivery window, and **3.46% (3,338)** suffer severe delays exceeding 7 days late.

4. **Geographic Concentration:**
   - **São Paulo (SP) is the logistical engine of Brazil**: 41.8% of platform demand (customer orders) and **70.3% of platform supply (seller shipments)** originate in SP.
   - Cross-regional shipments from SP into the North (AM, PA) and Northeast (BA, CE, PE) bear the brunt of delivery delays (late rates 11.4% – 18.2%, transit times >22 days).

5. **Customer Purchase Behavior:**
   - Marketplace repeat purchase rate is remarkably low: **3.12% of unique customers** (2,997 out of 96,096) placed more than one order during the 2-year window, accounting for 6.38% of total order volume.
   - Brazilian consumers finance **75.4% of credit card transactions in installments** (median 3 installments, max 24), scaling directly with purchase price.

---

## 2. What Surprised Us?

1. **The Premature Survey Trigger Phenomenon:**
   - **8,140 reviews were created before the order was recorded as delivered**.
   - Olist’s automated CRM triggers customer satisfaction surveys when the promised delivery estimate passes. Consequently, when an order is delayed, the customer receives an email asking "How was your purchase?" while the package is still stuck in transit.
   - In this overdue in-transit segment (5,335 orders), **70.89% of customers leave a 1- or 2-star review** (average score **1.98 stars**).
   - This single operational mechanism accounts for **3,782 low reviews — over 26% of all negative reviews on the entire marketplace**.

2. **The Illusion of Continuous Quality Degradation:**
   - Literature and casual analyses frequently claim that as Olist grew, customer satisfaction steadily deteriorated.
   - Our monthly time-series decomposition reveals that platform satisfaction remained stable around 4.10–4.20 stars across 2017 and 2018. The perceived "collapse" was actually an **acute capacity shock during the November 2017 Black Friday event**, where order volume surged 63% month-over-month (7,544 orders), overwhelming postal carriers and triggering a transient dip to 3.82 stars. Within 90 days, operations recovered to baseline.

3. **Freight Rate Counter-Intuition:**
   - Higher freight values do NOT buy faster delivery. Orders in the highest freight quintile take an average of **17.8 days** to arrive versus **10.4 days** for the lowest quintile. Freight in Brazil is a cost of distance and physical bulk, not expedited priority shipping.

---

## 3. What Appears Most Important?

1. **Delivery Delay Severity as the Sovereign Dissatisfaction Driver:**
   - The relationship between delay and customer reviews is profoundly non-linear:
     - Orders delivered early or on-time: **4.29 stars** (8.5% low reviews).
     - Orders 1 to 3 days late: **2.87 stars** (46.8% low reviews).
     - Orders > 7 days late: **1.62 stars** (82.7% low reviews).
   - Once an order exceeds 7 days late, customer satisfaction collapses entirely.

2. **Supply-Side Regional Asymmetry:**
   - Over 70% of sellers are located in São Paulo. Customers in distant states (e.g. Amazonas, Alagoas, Maranhão) pay **2.4x higher freight fees** and wait **2.8x longer for transit**, yet Olist applies uniform estimated delivery heuristics that disproportionately fail in these corridors.

---

## 4. What Appears Common / Obvious?

1. Late deliveries receive lower review scores than on-time deliveries.
2. Orders shipped over longer distances (high Haversine distance) take longer to deliver and incur higher freight charges.
3. Credit card transactions for expensive electronics or furniture are split into 6 to 12 installments more frequently than small fashion purchases.
4. Cancellations represent a tiny fraction (~0.6%) of total platform volume.

---

## 5. What Appears Differentiating?

1. **The Survey Trigger Distortion:**
   - Distinguishing between dissatisfaction caused by *package condition/product defect* vs. dissatisfaction caused by *surveying customers who have not received their package*.
2. **The 12-Day Expectation Buffer:**
   - Quantifying that Olist’s promised delivery date heuristic is systematically padded. Because 92.9% of orders arrive early, late orders violate customer expectations after an already lengthy holding period.
3. **Product Category Delay Resilience:**
   - Demonstrating that durable categories (furniture, home appliances) tolerate minor shipping delays with modest review penalties (-0.8 stars), whereas gifting and personal items (health & beauty, toys) suffer immediate rating collapse (-1.4 stars).
4. **Concentration Risk Exposure:**
   - Proving that over 66% of all negative reviews originate from less than 12% of orders characterized by specific regional cross-haul routes and delayed survey triggers.

---

## 6. What Hypotheses Gained Support?

| Hypothesis | Original Formulation | EDA Result | Status |
| :---: | :--- | :--- | :---: |
| **H2** | Customer dissatisfaction drops non-linearly with delivery delay severity. | Confirmed: 1-3d drops to 2.87; >7d collapses to 1.62. | **SUPPORTED** |
| **H3** | Estimated delivery dates are systematically conservative. | Confirmed: 92.9% arrive early; median is 11.95 days early. | **SUPPORTED** |
| **H4** | Inter-regional orders suffer higher severe delay rates. | Confirmed: SP $\to$ AM/BA has 3x higher failure rate than SP $\to$ SP. | **SUPPORTED** |
| **H5** | High freight cost does not guarantee superior speed or satisfaction. | Confirmed: Highest freight tier takes 17.8d vs 10.4d for lowest. | **SUPPORTED** |
| **H7** | Delivery delay is the primary driver of low reviews. | Confirmed: Spearman correlation with delay is -0.334; price/installments are <0.05. | **SUPPORTED** |
| **H8** | A small minority of segments accounts for disproportionate low reviews. | Confirmed: 5.4% in-transit surveyed orders account for 26.1% of negative reviews. | **SUPPORTED** |

---

## 7. What Hypotheses Weakened?

| Hypothesis | Original Formulation | EDA Result | Status |
| :---: | :--- | :--- | :---: |
| **H1** | Platform growth is accompanied by secular review score degradation. | Disproven as a secular trend: Average scores remained resilient (4.01-4.22); degradation was an acute capacity shock during Black Friday 2017. | **PARTIALLY SUPPORTED** |
| **H6** | Bulky/heavy categories have higher delay tolerance. | Mixed: Category resilience holds for 1-3 days late, but converges to universal failure (>80% low reviews) once delays exceed 7 days. | **PARTIALLY SUPPORTED** |

---

## 8. What Requires Formal Statistical Testing?

1. **Multivariate Odds Ratios (Module 17):**
   - We must control for product category, seller rating, order value, freight ratio, and customer state simultaneously using logistic regression to isolate the pure marginal effect of delivery delay versus survey timing.
2. **Inflection Point Splines (Module 7/17):**
   - Estimate the exact threshold (day 1, day 3, day 5, or day 7) where review sentiment transitions from negative to catastrophic.
3. **Corridor Delay Fixed Effects (Module 9/10):**
   - Econometrically separate carrier performance bottlenecks from geographical distance friction.

---

## 9. Which 3–5 Findings Should Drive the Next Analytical Modules?

1. **The Automated Survey Policy Fix:**
   - Quantifying the exact platform CSAT improvement achievable if Olist simply suppresses review surveys until a successful carrier delivery scan is registered.
2. **Logistics Bottlenecks in Long-Haul Corridors:**
   - Focusing operational interventions on the top 10 interstate routes responsible for the majority of severe delays (SP to Bahia, Rio de Janeiro, Ceará, and Minas Gerais).
3. **SLA Expectation Management & Promise Calibration:**
   - Redesigning delivery promise heuristics so that customers in challenging regions receive accurate dynamic windows rather than generic dates that trigger false delivery alarms.
4. **Seller Fulfillment Capacity & Black Friday Triage:**
   - Establishing seller dispatch monitoring protocols to prevent carrier handover delays during promotional surges.
