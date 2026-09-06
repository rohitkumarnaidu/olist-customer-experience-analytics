# MODULE 4: STATISTICAL & DIAGNOSTIC METHODOLOGY
## Formal Inferential Framework for E-Commerce Marketplace Diagnostics
**Project:** Gradient Learnings Data Analytics Hackathon 2026 — Olist Customer Experience Analytics  
**Document:** Research & Statistical Standards  
**Target:** Bridge between Exploratory Data Analysis and Root-Cause Modeling  
**Date:** September 2026  

---

## 1. Executive Overview & Purpose

The objective of Module 4 is to transition from **descriptive discovery** ("What patterns exist in the data?") to **formal inferential diagnostics** ("How strong are these relationships, what confounding factors explain them, where are the critical thresholds, and what are the operational accountabilities?").

In observational e-commerce data, raw correlations frequently mislead because operational variables (e.g., shipping distance, freight cost, order value, carrier handoff speed) are deeply intertwined with structural geography and customer expectations. This document formalizes the econometric, statistical, and diagnostic standards applied throughout Module 4 to prevent narrative inflation, control for confounding, detect non-linearities, and maintain strict inferential integrity.

---

## 2. Statistical Methodologies & Mathematical Formulations

### 2.1 Binary Logistic Regression
When the primary outcome of interest is binary—specifically whether an order results in a low review score ($Y = 1$ if $\text{review\_score} \le 2$, and $Y = 0$ otherwise)—ordinary least squares (OLS) violates classical Gauss-Markov assumptions (non-normality of residuals, heteroskedasticity, and predictions outside the $[0, 1]$ probability bound). We formulate the probability of a low review using the standard logit link function:

$$P(Y = 1 \mid \mathbf{X}) = \pi(\mathbf{X}) = \frac{1}{1 + \exp\left(-\left(\beta_0 + \sum_{j=1}^p \beta_j X_j\right)\right)}$$

In log-odds space, the relationship is linear:
$$\text{logit}(\pi) = \ln\left(\frac{\pi}{1 - \pi}\right) = \beta_0 + \beta_1 X_1 + \beta_2 X_2 + \dots + \beta_p X_p$$

* **Estimation Method:** Maximum Likelihood Estimation (MLE) via Newton-Raphson / BFGS numerical optimization.
* **Convergence Criterion:** Gradient norm $\|\nabla \ell(\beta)\| < 10^{-6}$ and non-singular Hessian matrix.
* **Goodness of Fit:** Evaluated via McFadden's Pseudo-$R^2$:
  $$R_{\text{McFadden}}^2 = 1 - \frac{\ln L_{\text{full}}}{\ln L_{\text{null}}}$$
  alongside Akaike Information Criterion (AIC) and Bayesian Information Criterion (BIC) for model selection.

---

### 2.2 Odds Ratios and Confidence Intervals
In logistic regression, raw coefficients $\beta_j$ represent the change in log-odds of the outcome per unit increase in predictor $X_j$. Because log-odds lack direct business interpretability, coefficients are transformed into **Odds Ratios (OR)**:

$$\text{OR}_j = \exp(\beta_j)$$

* **Interpretation:** For an unstandardized predictor, $\text{OR}_j$ represents the multiplicative change in the odds of receiving a low review score ($1$–$2$ stars) associated with a 1-unit increase in $X_j$, holding all other covariates constant.
  - $\text{OR} = 1.0$: No association.
  - $\text{OR} > 1.0$: Increased risk of customer dissatisfaction.
  - $\text{OR} < 1.0$: Decreased risk / protective factor.
* **Standardized Increments:** For continuous variables with large natural ranges (e.g., delivery delay days, distance in km, GMV), we report standardized increments:
  $$\text{OR}_{\Delta} = \exp(\beta_j \cdot \Delta)$$
  where $\Delta = 5\text{ days}$ for delay, $\Delta = 500\text{ km}$ for distance, and $\Delta = 1\text{ standard deviation}$ for continuous financial metrics.
* **Wald 95% Confidence Intervals:**
  $$\text{CI}_{95\%}(\text{OR}_j) = \left[\exp\left(\hat{\beta}_j - 1.96 \cdot \text{SE}(\hat{\beta}_j)\right), \; \exp\left(\hat{\beta}_j + 1.96 \cdot \text{SE}(\hat{\beta}_j)\right)\right]$$
* **Methodological Rule:** Never report a $p$-value without an accompanying Odds Ratio and 95% Confidence Interval. A statistically significant coefficient ($p < 0.05$) with an Odds Ratio of $1.001$ possesses zero practical business significance.

---

### 2.3 Multicollinearity & Variance Inflation Factor (VIF)
Multicollinearity occurs when two or more explanatory variables in a regression model are highly correlated, leading to unstable coefficient estimates, inflated standard errors, and sign inversions.

For each predictor $X_j$, the Variance Inflation Factor is computed by regressing $X_j$ against all remaining $p-1$ predictors:
$$X_j = \alpha_0 + \sum_{k \ne j} \alpha_k X_k + \epsilon_j \implies \text{VIF}_j = \frac{1}{1 - R_j^2}$$

* **Thresholds & Governance:**
  - $\text{VIF} < 2.5$: Low collinearity; completely safe.
  - $2.5 \le \text{VIF} < 5.0$: Moderate collinearity; acceptable with monitoring.
  - $\text{VIF} \ge 5.0$: High collinearity; requires variable selection or dimension reduction.
  - $\text{VIF} \ge 10.0$: Severe collinearity; strictly prohibited in final models.
* **Domain Redundancies Addressed:**
  - `order_gmv` vs `payment_value_total` ($r = 0.999$): Retain $\ln(\text{GMV} + 1)$ for commercial ticketing; exclude redundant payment value.
  - `item_price_total` vs `order_gmv` ($r = 0.98$): Retain `order_gmv` and express freight as a ratio (`freight_share_pct`).
  - `haversine_distance_km` vs `is_interstate`: Evaluate joint stability.

---

### 2.4 Breakpoint Detection & Piecewise Segmented Regression
The relationship between delivery delay and customer satisfaction is non-linear: modest delays (1–2 days) may trigger minor frustration, but extended delays cross an emotional threshold into acute dissatisfaction.

To empirically detect where satisfaction deteriorates sharply without imposing arbitrary thresholds, we specify a continuous piecewise linear model with an unknown change-point $\tau$:

$$y_i = \beta_0 + \beta_1 x_i + \beta_2 (x_i - \tau)_+ + \mathbf{\gamma}' \mathbf{Z}_i + \epsilon_i$$

where $(x_i - \tau)_+ = \max(0, x_i - \tau)$ is the ramp function:
$$(x_i - \tau)_+ = \begin{cases} 0 & \text{if } x_i \le \tau \\ x_i - \tau & \text{if } x_i > \tau \end{cases}$$

* **Interpretation:**
  - $\beta_1$: The baseline slope of satisfaction prior to the threshold ($x \le \tau$).
  - $\beta_1 + \beta_2$: The secondary slope of satisfaction after exceeding the threshold ($x > \tau$).
  - $\beta_2$: The change in slope (inflection magnitude). If $\beta_2 < 0$, satisfaction decline accelerates beyond $\tau$.
* **Estimation:** We execute a profile likelihood grid search over candidate breakpoints $\tau \in [0.5, 10.0]$ days in steps of $0.5$ days, minimizing the residual sum of squares (RSS) and Akaike Information Criterion (AIC).
* **Validation:** Compared against non-parametric Locally Weighted Scatterplot Smoothing (LOWESS) with span $\alpha = 0.3$.

---

### 2.5 Statistical Significance vs. Practical Significance (Effect Sizes)
With large administrative datasets ($N \approx 96,000$), standard hypothesis tests are overpowered: virtually every non-zero coefficient produces $p < 0.001$. We enforce formal effect size quantification:

1. **Partial Eta-Squared ($\eta_p^2$) in ANOVA:**
   $$\eta_p^2 = \frac{\text{SS}_{\text{effect}}}{\text{SS}_{\text{effect}} + \text{SS}_{\text{residual}}}$$
   - Benchmarks: Small $= 0.01$ ($1\%$), Medium $= 0.06$ ($6\%$), Large $= 0.14$ ($14\%$).
2. **Cramer's $V$ for Categorical Associations:**
   $$V = \sqrt{\frac{\chi^2}{N \cdot \min(R - 1, C - 1)}}$$
   - Benchmarks: Small $= 0.10$, Medium $= 0.30$, Large $= 0.50$.
3. **Cohen's $d$ for Two-Group Comparisons:**
   $$d = \frac{\bar{X}_1 - \bar{X}_2}{s_{\text{pooled}}}$$
   - Benchmarks: Small $= 0.20$, Medium $= 0.50$, Large $= 0.80$.

---

## 3. Analytical Population Definitions

To ensure complete transparency and prevent denominator contamination across models, we establish 5 standardized, nested populations:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                       STANDARDIZED POPULATION REGISTER                       │
├──────────────┬───────────────┬───────────────────────────────────────────────┤
│ POPULATION   │ COUNT         │ DEFINITION & CRITERIA                         │
├──────────────┼───────────────┼───────────────────────────────────────────────┤
│ Population A │ 99,441 orders │ Complete Canonical Base (All orders)          │
│ Population B │ 96,478 orders │ Delivered Orders (order_status == 'delivered')│
│ Population C │ 96,470 orders │ Eligible Delivery (Delivered + valid date)    │
│ Population D │ 98,673 orders │ Reviewed Orders (has_review == True)          │
│ Population E │ 95,831 orders │ Primary Modeling Sample: Delivered + Reviewed │
└──────────────┴───────────────┴───────────────────────────────────────────────┘
```

* **Core Modeling Sample (Population E, $N = 95,831$):** Represents orders that were physically delivered and received a customer review. This sample forms the bedrock for all logistic regressions, delivery accountability decompositions, and threshold analyses.
* **Population Rules:**
  - Non-delivered orders (cancelled, unavailable, in-transit) are analyzed separately in fulfillment funnel diagnostics and never mixed into delivery duration models.
  - The exact population denominator must be documented in every table and figure.

---

## 4. Observational Causal Limitations & Confounding Structure

### 4.1 The Causal DAG of E-Commerce Satisfaction
We formalize the underlying data generating process using a Directed Acyclic Graph (DAG):

```text
  [Geographic Distance / Regional Infrastructure]
          │                                  │
          ▼                                  ▼
[Carrier Transit Duration]          [Freight Cost Share]
          │                                  │
          ▼                                  │
[Delivery Delay vs SLA]                      │
    │               │                        │
    │               ▼                        │
    │    [Premature Survey Trigger]          │
    │               │                        │
    ▼               ▼                        ▼
     ───────────────────► [Customer Review Score] ◄─── [Product Quality / GMV]
```

### 4.2 Distinguishing Mediation from Confounding
1. **The Survey Timing Dilemma:**
   - Pre-delivery surveys occur when an order is delayed past its estimated delivery date while still in transit ($N = 5,336$).
   - *Confounding Risk:* Does the survey cause the negative review, or does severe delivery delay cause both the premature survey and the negative review?
   - *Methodological Solution:* We use **nested hierarchical regression** and **delay-matched stratification**. We compare customers experiencing the exact same number of delay days, differing only in whether their survey was completed before or after delivery.
2. **The Freight Price Illusion:**
   - *Observation:* Customers paying higher freight have slightly lower review scores in raw bivariate data.
   - *Confounding:* High freight orders travel across continental distances ($> 2,000\text{ km}$) from São Paulo to the North/Northeast and carry heavy volumetric goods.
   - *Solution:* Conditioning on spatial distance and delivery duration eliminates the spurious freight-satisfaction penalty.

---

## 5. Multiple Testing & False Discovery Governance

Module 4 executes multiple hypothesis tests across geographic corridors, product categories, and nested model specifications. To guard against Family-Wise Error Rate (FWER) inflation and false positives:
* Primary inferences are drawn from pre-specified nested models, not post-hoc data dredging.
* For exploratory pairwise category or corridor comparisons ($m > 10$), we apply the **Benjamini-Hochberg (BH) False Discovery Rate (FDR)** procedure at $\alpha = 0.05$:
  $$p_{(i)} \le \frac{i}{m} Q$$
* Findings are verified through sensitivity analysis across alternative outcome thresholds ($Y \in \{\le 1\star, \le 2\star, \le 3\star\}$).

---

## 6. Summary of Methodological Commitments

1. **No Causal Overclaiming:** Observational logistic models report *adjusted associations*, not unvarnished counterfactual proof.
2. **Effect Sizes Accompany All Inferences:** Every reported regression displays an Odds Ratio, 95% Confidence Interval, and standard error.
3. **Multicollinearity Audited Prior to Modeling:** Predictors with $\text{VIF} \ge 5.0$ are pruned or transformed.
4. **Population Denominators Explicitly Declared:** Every table states whether it uses Population A, B, C, D, or E.
5. **Reproducibility Guarantee:** All results derive deterministically from `data/processed/analytical_model.parquet`.
