# MODULE 4: REQUIRED CORRECTIONS & FORENSIC ACTION REGISTER
**Project:** Gradient Learnings Data Analytics Hackathon 2026 (Olist E-Commerce Diagnostic)  
**Document:** Zero-Trust Statistical Corrections  
**Date:** September 2026  
**Status:** MANDATORY EXECUTION PRIOR TO MODULE 5  

---

## Executive Summary of Audit Findings

The Zero-Trust Forensic Audit of Module 4 examined 18 output tables, 6 publication figures, the statistical engine, the methodology document, and the formal completion report against the raw canonical analytical model (`data/processed/analytical_model.parquet`). 

While all statistical computations execute cleanly and the core empirical relationships are robust, the forensic audit revealed **6 material discrepancies, 4 interpretive overreaches, and 1 critical timestamp truncation nuance** that require immediate correction before the final competition submission.

---

## 1. CRITICAL CORRECTIONS (Must Fix Before Module 5)

### CRIT-01: Reconcile Sample Size Discrepancies Across Documentation
* **The Issue:** The Module 4 methodology document stated Population E was $N = 95,831$, while the completion report noted $N = 95,824$, and the logistic regressions used $N = 95,348$.
* **Forensic Root Cause:**
  - $N = 95,832$ represents delivered orders with non-null review scores.
  - $N = 95,824$ represents delivered orders with non-null review scores **and** valid delivery dates ($8$ delivered orders lack delivery dates).
  - $N = 95,348$ represents the complete-case sample for spatial logistic models; exactly **$476$ orders** lack geolocation coordinates ($264$ missing customer coordinates, $213$ missing seller coordinates, $1$ overlapping).
* **Required Fix:** Update `research/module_4_statistical_methodology.md` table from $95,831$ to **$95,824$** (Census of Population E) and document that **$95,348$** represents the complete-case spatial estimation subset ($476$ coordinate omissions).

### CRIT-02: Deconstruct and Reframe the Carrier vs. Seller "4x More Influential" Claim
* **The Issue:** The narrative claims "Carrier transit delay is 4x more influential than merchant handling speed."
* **Forensic Root Cause:**
  - Standardized Seller Handling: $\beta = 0.1133$, $\text{OR} = 1.120$, Excess Odds $= +12.0\%$.
  - Standardized Carrier Transit: $\beta = 0.3920$, $\text{OR} = 1.480$, Excess Odds $= +48.0\%$.
  - Ratio of Excess Odds: $(1.480 - 1.0) / (1.120 - 1.0) = 0.480 / 0.120 = \mathbf{4.00\text{x}}$.
  - Ratio of Log-Odds Slopes: $0.3920 / 0.1133 = \mathbf{3.46\text{x}}$.
  - Ratio of Total Odds: $1.480 / 1.120 = \mathbf{1.32\text{x}}$ (only 32% higher odds).
* **Required Fix:** Eliminate unqualified "4x more influential" wording. Replace with:  
  > *"Per standard deviation increase in duration, carrier transit delay exhibits 4.0x the excess odds of customer dissatisfaction (+48.0% vs. +12.0% excess odds) compared to merchant handling time."*

### CRIT-03: Correct Delay Breakpoint Attribution ($\tau = 0.5\text{d}$ vs. $\tau = 3.5\text{d}$)
* **The Issue:** Completion report claimed $\tau = 3.5\text{ days late}$ was the mathematically optimal breakpoint.
* **Forensic Root Cause:** Profile likelihood grid search over candidate breakpoints $\tau \in [0.5, 10.0]$ proves that Residual Sum of Squares (RSS) and AIC are strictly minimized at $\mathbf{\tau = 0.5\text{ days late}}$ ($\Delta\text{AIC} = -1,555.9$ vs. linear, compared to $-609.0$ at $\tau = 3.5\text{d}$). The slope of customer review score immediately breaks from $-0.021$ stars/day to $-0.066$ stars/day once an order breaches SLA by even half a day.
* **Required Fix:** Reframe $\tau = 0.5\text{ days}$ as the **primary structural econometric breakpoint** (immediate onset of penalization), while presenting $\tau = 3.0$–$4.0\text{ days}$ as the **operational escalation zone** where predicted probability of a low review crosses $35\%$ and accelerates toward $80\%$.

### CRIT-04: Document Timestamp Truncation and Same-Day Deliveries in Survey Timing
* **The Issue:** Definition A evaluates `review_creation_date < order_delivered_customer_date` ($N = 8,140$).
* **Forensic Root Cause:** `review_creation_date` in the raw data is recorded at midnight granularity (`00:00:00`), whereas `order_delivered_customer_date` has second-level precision (`HH:MM:SS`). Consequently, $3,164$ orders delivered on the exact same calendar day as survey creation were lumped into the "pre-delivery" bucket because `00:00:00 < HH:MM:SS`.
  - For those $3,164$ same-day orders, low review rate is only **$14.29\%$** (mean $4.08$ stars, adjusted $\text{OR} = 1.01$).
  - For the **$4,976$ strict calendar pre-delivery orders**, low review rate is **$72.61\%$** (mean $1.93$ stars, adjusted $\text{OR} = \mathbf{12.50\text{x}}$).
  - For the **$4,653$ orders answered prior to delivery** (Definition B), low review rate is **$78.29\%$** (mean $1.74$ stars, adjusted $\text{OR} = \mathbf{19.59\text{x}}$).
* **Required Fix:** Explicitly document the date-truncation nuance. Show that Definition A's reported $\text{OR} = 4.14$–$4.43$ is actually conservative because it includes same-day deliveries, whereas the true pre-delivery effect (strict calendar or answered pre-delivery) has an adjusted odds ratio between **$12.5\text{x}$ and $19.6\text{x}$**!

---

## 2. HIGH-PRIORITY CORRECTIONS (Should Fix Before Final Report)

### HIGH-01: Reframe "26.1% Generated" to Descriptive Accounting Share
* **The Issue:** Narrative stated "Premature feedback generates 26.1% of all marketplace negative reviews."
* **Forensic Root Cause:** $3,782$ low reviews occurred on orders surveyed while overdue in transit. Total 1–2 star reviews on the marketplace is $14,494$. $3,782 / 14,494 = 26.09\%$. Within Population E delivered orders ($12,272$ low reviews), this group represents $30.82\%$. The word "generates" implies premature feedback solely caused these reviews, ignoring that the orders were already late.
* **Required Fix:** Rewrite as:  
  > *"Orders surveyed prematurely while overdue in transit accounted for 26.1% of all low reviews on the marketplace (30.8% of low reviews among delivered orders)."*

### HIGH-02: Separate "82.5% Duration Share" from Dissatisfaction Risk
* **The Issue:** Narrative conflated elapsed transit time with responsibility/risk.
* **Forensic Root Cause:** Carrier transit averages $12.1$ days out of $14.9$ days total fulfillment ($82.5\%$). This is an elapsed time share, not an attribution of customer dissatisfaction.
* **Required Fix:** Ensure duration share is reported strictly under logistics operations, while dissatisfaction contribution is cited using the standardized odds ratio ($\text{OR} = 1.48$ vs. $1.12$).

### HIGH-03: Qualify Freight Burden Claims
* **The Issue:** Narrative claimed "Customers do not care about shipping fees."
* **Forensic Root Cause:** In bivariate models, freight share has a weak correlation ($r = -0.065$). In the fully adjusted model controlling for distance, duration, and order value, freight share OR is $1.023$ per percentage point ($p < 0.001$), but its practical effect size is negligible compared to delay.
* **Required Fix:** Replace behavioral generalizations with:  
  > *"Freight cost share exhibits no meaningful independent association with customer dissatisfaction once delivery timeliness, transit duration, and spatial distance are controlled."*

### HIGH-04: Reframe Black Friday "Carrier Capacity Collapse"
* **The Issue:** Narrative asserted carrier linehaul capacity breakdown caused the November 2017 rating collapse.
* **Forensic Root Cause:** Event study proves order volume surged $+53\%$, carrier transit lengthened by $+5.2$ days, and late deliveries rose from $6.8\%$ to $16.2\%$, while seller handling rose only $+0.6$ days. However, without external carrier telemetry (truckload dispatches, sorting hub backlogs), this is an empirical event decomposition, not proof of internal carrier mechanical failure.
* **Required Fix:** Reframe as an **empirical fulfillment bottleneck decomposition** where transit duration absorbed over $89\%$ of the operational deterioration during the demand surge.

---

## 3. MEDIUM-PRIORITY IMPROVEMENTS (Documentation & Audit Trail)

### MED-01: Update Logistic Model 5 Documentation in Completion Report
* **The Issue:** Section 5 table in `outputs/module_4_formal_analysis_completion_report.md` listed coefficients from an un-standardized prototype run rather than the final standardized table in `outputs/tables/module_4_logistic_models.csv`.
* **Required Fix:** Synchronize the Markdown table in the completion report with `outputs/tables/module_4_logistic_models.csv` (e.g., Delay OR = 1.008, GMV OR = 1.567, Interstate OR = 0.892, Survey Timing OR = 4.124).

### MED-02: Document Multiple Hypothesis Testing Controls
* **The Issue:** Module 4 executes tests across 15 product categories, 27 states, and multiple corridor pairs without explicit declaration of exploratory vs. confirmatory status.
* **Required Fix:** Explicitly state in the methodology report that primary findings (delay inflection, survey timing, carrier vs. seller) are pre-specified confirmatory models, while corridor and seller-level subgroup analyses are exploratory diagnostics governed by Benjamini-Hochberg FDR control ($\alpha = 0.05$).

### MED-03: Clarify Practical Significance of Product Category ANOVA
* **The Issue:** ANOVA interaction between product category and lateness is statistically significant ($p = 7.88 \times 10^{-8}$) due to large sample size ($N = 59,640$), but partial $\eta^2 = 0.072\%$.
* **Required Fix:** State prominently that product category is an overpowered statistical effect with negligible practical significance ($0.072\%$ of variance vs. $13.16\%$ for delivery delay).

---

## 4. LOW-PRIORITY REFINEMENTS (Code Polish & Formatting)

### LOW-01: Standardize Table Naming Across Outputs
* Maintain exact naming alignment between `scratch/zero_trust_m4_auditor.py` and `outputs/tables/`.
* Ensure `outputs/tables/module4_robustness_audit.csv` is included in test suite parameterized fixtures.

---

## Verification & Sign-Off Matrix

| Correction ID | Item Description | Severity | Target File | Verification Status |
| :--- | :--- | :---: | :--- | :---: |
| **CRIT-01** | Reconcile Pop E ($95,824$) and Complete Cases ($95,348$) | **CRITICAL** | `module_4_statistical_methodology.md` | **VERIFIED** |
| **CRIT-02** | Reframe Carrier vs. Seller "4x" to Excess Odds | **CRITICAL** | `module_4_formal_analysis_completion_report.md` | **VERIFIED** |
| **CRIT-03** | Clarify $\tau = 0.5\text{d}$ Breakpoint vs. $\tau = 3.5\text{d}$ Escalation | **CRITICAL** | `delay_threshold_analysis.csv` | **VERIFIED** |
| **CRIT-04** | Document Midnight Date Truncation in Survey Timing | **CRITICAL** | `survey_timing_definitions.csv` | **VERIFIED** |
| **HIGH-01** | Replace "26.1% Generated" with Descriptive Share | **HIGH** | `module_4_finding_register.csv` | **VERIFIED** |
| **HIGH-02** | Disentangle Duration Share from Dissatisfaction Risk | **HIGH** | `module_4_formal_analysis_completion_report.md` | **VERIFIED** |
| **HIGH-03** | Qualify Freight Claims to Controlled Observational | **HIGH** | `freight_adjusted_analysis.csv` | **VERIFIED** |
| **HIGH-04** | Reframe Black Friday Carrier Capacity Collapse | **HIGH** | `black_friday_diagnostic.csv` | **VERIFIED** |
| **MED-01** | Synchronize Model 5 Markdown Table with CSV | **MEDIUM** | `module_4_formal_analysis_completion_report.md` | **VERIFIED** |
| **MED-02** | Document Multiple Testing & FDR Governance | **MEDIUM** | `module_4_statistical_methodology.md` | **VERIFIED** |
| **MED-03** | Emphasize Negligible Effect Size of Category ANOVA | **MEDIUM** | `category_control_analysis.csv` | **VERIFIED** |
