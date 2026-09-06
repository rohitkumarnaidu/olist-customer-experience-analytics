# Dataset Structure, Table Grain & Relational Architecture
**Project:** Gradient Learnings — Data Analytics Hackathon 2026 (Olist)  
**Module:** MODULE 1 — DATA ACQUISITION & INVENTORY  
**Status:** Validated with Empirical Dataset Execution

---

## 1. Relational Map and Table Grains

The Olist e-commerce dataset is composed of 9 relational tables centered around customer purchases in Brazil between September 2016 and October 2018.

```
                    ┌─────────────────────────┐
                    │    olist_customers      │
                    │  Grain: Customer Order  │
                    │   PK: customer_id       │
                    └────────────┬────────────┘
                                 │ 1:1
                                 ▼
┌──────────────────────────┐    ┌─────────────────────────┐    ┌──────────────────────────┐
│   olist_order_reviews    │    │      olist_orders       │    │   olist_order_payments   │
│ Grain: Review Submission │◄───┤    Grain: Order Unit    ├───►│  Grain: Payment Attempt  │
│      PK: review_id       │1:N │      PK: order_id       │1:N │PK: order_id+payment_seq  │
└──────────────────────────┘    └────────────┬────────────┘    └──────────────────────────┘
                                             │ 1:N
                                             ▼
                                ┌─────────────────────────┐
                                │    olist_order_items    │
                                │   Grain: Order Line     │
                                │PK: order_id+order_item_id
                                └───────┬─────────┬───────┘
                                    N:1 │         │ N:1
                    ┌───────────────────┘         └───────────────────┐
                    ▼                                                 ▼
        ┌───────────────────────┐                         ┌───────────────────────┐
        │    olist_products     │                         │     olist_sellers     │
        │     Grain: SKU        │                         │ Grain: Merchant Entity│
        │    PK: product_id     │                         │     PK: seller_id     │
        └───────────┬───────────┘                         └───────────┬───────────┘
                N:1 │                                                 │
                    ▼                                                 │
        ┌───────────────────────┐                                     │
        │ product_cat_trans     │                                     │
        │ Grain: Category Term  │                                     │
        │PK: product_cat_name   │                                     │
        └───────────────────────┘                                     │
                                                                      │
                    ┌─────────────────────────────────────────────────┘
                    ▼
        ┌───────────────────────┐
        │   olist_geolocation   │
        │Grain: Coordinate Trace│
        │  PK: NONE (1:N zip)   │
        └───────────────────────┘
```

---

## 2. Table-by-Table Architectural Specifications

| Table | Official File | Actual Rows | Inferred Grain | Primary Key | Key Uniqueness |
| :--- | :--- | :---: | :--- | :--- | :---: |
| **Orders** | `olist_orders_dataset.csv` | 99,441 | Single commercial order | `order_id` | **100.0%** |
| **Order Items** | `olist_order_items_dataset.csv` | 112,650 | Individual product line item | `order_id` + `order_item_id` | **100.0%** |
| **Payments** | `olist_order_payments_dataset.csv` | 103,886 | Sequential payment installment/voucher | `order_id` + `payment_sequential` | **100.0%** |
| **Reviews** | `olist_order_reviews_dataset.csv` | 99,224 | Survey feedback submission | `review_id` | **99.18%** (814 dups) |
| **Customers** | `olist_customers_dataset.csv` | 99,441 | Order transaction customer instance | `customer_id` | **100.0%** |
| **Products** | `olist_products_dataset.csv` | 32,951 | Distinct catalog item (SKU) | `product_id` | **100.0%** |
| **Sellers** | `olist_sellers_dataset.csv` | 3,095 | Distinct marketplace merchant | `seller_id` | **100.0%** |
| **Geolocation** | `olist_geolocation_dataset.csv` | 1,000,163 | Lat/Lng coordinate log per zip prefix | *None (Non-unique)* | **0.0%** (19,015 zips) |
| **Translation** | `product_category_name_translation.csv` | 71 | Category name translation entry | `product_category_name` | **100.0%** |

---

## 3. Important Cardinality & One-to-Many Relationships

### 1. Orders vs. Order Items ($1:N$)
- **Empirical Evidence:** 98,666 distinct orders appear in `order_items`. 
- **Multi-Item Reality:** Exactly **9,803 orders (9.94%)** contain more than 1 item, accounting for **13,984 additional item rows** (up to 21 items in an order).
- **Zero-Item Orders:** Exactly **775 orders** in `orders` (99,441 - 98,666) have zero records in `order_items` because they were canceled or unavailable before items were fulfilled.
- **Architectural Rule:** Never merge raw items directly to orders. Always aggregate item metrics (total price, total freight, total item count, dominant category) before joining.

### 2. Orders vs. Payments ($1:N$)
- **Empirical Evidence:** 99,440 distinct orders appear in `order_payments` (exactly 1 order has no payment record).
- **Split Tenders:** **2,961 orders (2.98%)** have multiple payment records (spanning up to 29 payment records for orders split across credit cards and multiple vouchers).
- **Architectural Rule:** Pre-aggregate payment values, max installments, and dominant payment method to the `order_id` grain before merging.

### 3. Orders vs. Reviews ($1:N$)
- **Empirical Evidence:** Exactly 98,673 distinct orders have reviews.
- **Multiple Reviews:** **547 orders** received multiple review surveys. Furthermore, `review_id` has **814 duplicates** across the dataset where identical review IDs were issued for multi-item orders.
- **Architectural Rule:** Deduplicate reviews by taking the latest `review_answer_timestamp` per `order_id`.

### 4. Customers ($1:N$ Person-to-Order)
- **Empirical Evidence:** While `customer_id` has 99,441 distinct values, `customer_unique_id` contains **96,096 distinct human beings**.
- **Repeat Customers:** Exactly **2,997 customers** (3.12%) made multiple orders (ranging up to 17 orders by a single individual).
- **Architectural Rule:** Any customer lifetime, retention, or repeat purchase KPI must group by `customer_unique_id`, never `customer_id`.

### 5. Geolocation Multiplicity ($1:N$)
- **Empirical Evidence:** 19,015 unique 5-digit zip prefixes span 1,000,163 rows (an average of **52.6 coordinates per zip prefix**, with a maximum of **1,146 rows for a single zip code**).
- **Severe Join Hazard:** A direct relational join on `zip_code_prefix` multiplies order rows by up to 1,146x, destroying the order grain and falsifying financial totals.
- **Spatial Outliers:** 29 latitude rows and 37 longitude rows lie outside Brazil's bounding box (e.g. positive latitudes up to $+45.06^\circ$).
- **Architectural Rule:** Aggregate geolocation to mean centroid $(\bar{\text{lat}}, \bar{\text{lng}})$ per prefix after clipping to valid Brazilian coordinates $(\text{lat} \in [-35, 6], \text{lng} \in [-75, -33])$.

### 6. Translation Mapping Gap
- **Empirical Evidence:** The `products` table has 73 distinct Portuguese categories, but `product_category_name_translation.csv` only contains 71.
- **Missing Categories:** `'pc_gamer'` and `'portateis_cozinha_e_preparadores_de_alimentos'` are completely absent from the official translation table.
- **Architectural Rule:** Supply explicit fallback translations in Module 3.
