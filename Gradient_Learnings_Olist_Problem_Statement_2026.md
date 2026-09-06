# Gradient Learnings Data Analytics Hackathon 2026
# Official Problem Statement

> Source: Gradient Learnings Data Analytics Hackathon 2026 Problem Statement / Notion page.
>
> Dataset: [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

---

# Data Set Link

[Click Here](https://docs.google.com/spreadsheets/d/185kNKyDzoxsugKtqPcIxKG9B4yswTHzO/edit?usp=sharing&ouid=104233941355739767562&rtpof=true&sd=true)

---

# About This Dataset

This hackathon uses a real, publicly released dataset rather than a synthetic one: approximately 100,000 orders placed on the Olist marketplace in Brazil between September 2016 and October 2018. It was originally published by Olist, a company that connects small and medium Brazilian merchants to major online marketplaces through a single contract, and has been anonymized by Olist itself before release. Customer and seller identities are hashed IDs, and any company or partner names that appeared in review text have been replaced with fictional names.

> **Source and license:** Brazilian E-Commerce Public Dataset by Olist, originally published on Kaggle ([kaggle.com/datasets/olistbr/brazilian-ecommerce](http://kaggle.com/datasets/olistbr/brazilian-ecommerce)) under a Creative Commons Attribution-NonCommercial-ShareAlike license. Verify the current license terms on the Kaggle page before any commercial or redistribution use. This is real commercial data released for public analysis and education, not data collected or generated for this hackathon.

---

# Problem Statement

## Business Background

Olist is a Brazilian e-commerce platform that acts as a marketplace integrator: small and medium merchants across Brazil sign a single contract with Olist to sell through major marketplaces without negotiating each one individually. When a customer buys a product through an Olist-connected store, the responsible seller is notified to fulfill the order and ships it using Olist’s logistics partners. Once the order is delivered, or once the estimated delivery date has passed, the customer receives a satisfaction survey by email where they can leave a 1 to 5 star review and, optionally, written comments.

## The Business Challenge

Olist’s leadership has approximately two years of order history (September 2016 to October 2018) covering orders, items, payments, products, sellers, customers, reviews, and geolocation data. Review scores, delivery timing, seller performance, and payment behavior all vary considerably across this period, across product categories, and across Brazil’s states, but no single, consolidated analysis has connected these dimensions together. Leadership wants to understand what is actually shaping the customer experience on the platform, and where the clearest opportunities are to improve it as Olist continues to scale to more sellers and more regions of Brazil.

## Your Role

You are a Data Analyst supporting Olist’s operations and customer experience teams. You have been given the platform’s order, product, payment, seller, customer, and review data and asked to independently investigate what is really driving performance and customer satisfaction on the marketplace.

## Objective

Determine how the marketplace has performed over the available time period, what factors are associated with customer satisfaction and dissatisfaction, where performance varies most across sellers, geography, categories, and payment behavior, and what Olist should prioritize as a result. Use evidence from the data rather than assumptions. No answer is provided here; that is for you to find.

## Core Questions to Investigate

Focus your primary analysis on these six questions. Together they should form the main analytical story of your submission.

### 1. Marketplace Performance Over Time

How have order volume, revenue, and review scores trended across the available time period? Do they all tell the same story?

### 2. Delivery Performance and Customer Satisfaction

How does delivery timing (relative to the estimated delivery date) relate to review scores? Does this hold across different categories and regions, or is it concentrated somewhere specific?

### 3. Seller and Geographic Patterns

Sellers and customers are not evenly distributed across Brazil. How does this geographic pattern relate to delivery performance, freight cost, or customer satisfaction?

### 4. Product Category Performance

How do order volume, price, and review scores differ across product categories? Are any categories notably stronger or weaker than the platform average?

### 5. Payment Behavior

How do payment type and installment choices relate to order value, and do they appear connected to anything else in the customer’s experience?

### 6. Root Cause Analysis

Identify the most important factors associated with low review scores on this platform. Use evidence to distinguish between factors that appear to be primary drivers and factors that appear to be secondary or contributing. You are not expected to prove a single cause; more than one factor likely contributes.

---

# Optional Deep-Dive Questions

> Participants are not expected to answer every question. The questions are provided as analytical directions. Participants should focus on building the strongest evidence-based business story they can within the hackathon timeframe.

These are additional analytical directions you may explore if time allows. A strong submission does not need to touch all, or even most, of them.

- **Repeat Customers:** The dataset distinguishes an order-level `customer_id` from a person-level `customer_unique_id`. What does this reveal about repeat purchase behavior, and how valuable are repeat customers relative to one-time buyers?
- **Freight and Product Characteristics:** How do product weight and dimensions relate to freight cost, and does this vary by distance between seller and customer?
- **Seller-Level Performance:** Beyond category and geography, do individual sellers show meaningfully different performance from one another, controlling for what they sell and where they ship?
- **Review Text (Advanced, Optional):** For reviews that include written comments, does anything in the text add to what the numeric score already tells you?
- **Anomalies:** Are there orders, sellers, or categories that stand out as unusual (extreme delays, unusual pricing, unusually high or low review volume) and worth flagging separately?

---

# Expected Outcome

Olist’s leadership wants a clear, evidence-based picture of three things: how the marketplace is actually performing, which factors appear to be associated with customer satisfaction and dissatisfaction (and which of those look like primary drivers versus secondary contributors), and what Olist should prioritize to improve the platform experience as it continues to grow. You are not expected to prove causation from observational data; a well-reasoned, well-evidenced case for what is likely going on is what a strong submission looks like.

---

# Dataset Overview

You will receive nine related CSV files covering orders placed between September 2016 and October 2018:

| File | Rows | Grain |
|---|---:|---|
| `olist_orders_dataset.csv` | 99,441 | 1 row per order |
| `olist_order_items_dataset.csv` | 112,650 | 1 row per item within an order |
| `olist_order_payments_dataset.csv` | 103,886 | 1 row per payment record (an order can have more than one) |
| `olist_order_reviews_dataset.csv` | 100,000 | 1 row per review |
| `olist_customers_dataset.csv` | 99,441 | 1 row per order-level customer record |
| `olist_products_dataset.csv` | 32,951 | 1 row per product |
| `olist_sellers_dataset.csv` | 3,095 | 1 row per seller |
| `olist_geolocation_dataset.csv` | 1,000,163 | multiple rows per zip code prefix (lat/lng readings) |
| `product_category_name_translation.csv` | 71 | 1 row per category name pair |

The dataset structure, table relationships, column definitions, and known real-world data quality characteristics are documented in full later in this document. There is no target or label column; this is an open analytics challenge, not a prediction task.

---

# Participant Deliverables

## 1. Google Colab Notebook

Data Understanding, Data Cleaning, Exploratory Data Analysis, Analysis (addressing the Core Questions, and any Optional Deep-Dive questions you choose to pursue), Visualizations, and Key Findings. Should run top to bottom without errors.

## 2. Analysis Report

Problem Understanding, Analytical Approach, Key Insights, Supporting Visualizations, Business Findings, and Actionable Recommendations.

## 3. Three-Minute Video

Explain, in this order: the business problem, your analytical approach, your most important insight or insights, and your recommendations, as if presenting to Olist’s operations and customer experience leadership.

---

# A Note on Skill Levels

This dataset and question set is designed to work for beginners through advanced analysts on the same data:

- **Beginner-friendly:** data cleaning, KPI calculation, exploratory data analysis, and straightforward visualizations are enough to produce a genuinely useful answer to the Core Questions.
- **Intermediate:** joining across multiple tables, segmentation by category or region, and time trend analysis will surface more of what the data has to offer.
- **Advanced:** statistical testing, geographic distance calculations from the geolocation table, cohort or repeat-purchase analysis, and text analysis of review comments are welcome where they genuinely fit, but none of them are required to do well.

There is no minimum technique requirement at any level. A focused, well-evidenced answer to the six Core Questions is a complete and competitive submission on its own.

---

# Dataset File Structure

## `olist_orders_dataset.csv` (core fact table)

**Purpose:** The central record of each order, with every status timestamp from purchase through delivery.

**Rows:** 99,441

**Columns:** 8

**Primary Key:** `order_id`

**Foreign Keys:** `customer_id` references `customers.customer_id`

**Date Range:** `order_purchase_timestamp` spans September 4, 2016 to October 17, 2018

---

## `olist_order_items_dataset.csv`

**Purpose:** Line-item detail for each order. An order with three units of the same product has three rows here.

**Rows:** 112,650

**Columns:** 6

**Primary Key:** composite: `order_id` and `order_item_id`

**Foreign Keys:** `order_id` references orders.`order_id`; `product_id` references products.`product_id`; `seller_id` references sellers.`seller_id`

---

## `olist_order_payments_dataset.csv`

**Purpose:** How each order was paid for. About 4,400 orders have more than one payment record (split or combined payment methods).

**Rows:** 103,886

**Columns:** 5

**Primary Key:** composite: `order_id` and `payment_sequential`

**Foreign Keys:** `order_id` references orders.`order_id`

---

## `olist_order_reviews_dataset.csv`

**Purpose:** The post-purchase satisfaction survey: a 1 to 5 star score and, optionally, written comments.

**Rows:** 100,000

**Columns:** 7

**Primary Key:** `review_id`

**Foreign Keys:** `order_id` references orders.`order_id`

---

## `olist_customers_dataset.csv`

**Purpose:** Customer location for each order. Note the important distinction between `customer_id` and `customer_unique_id` explained in the Data Quality section.

**Rows:** 99,441

**Columns:** 5

**Primary Key:** `customer_id`

**Foreign Keys:** none

---

## `olist_products_dataset.csv`

**Purpose:** The product catalog, including category and the physical dimensions used to calculate freight.

**Rows:** 32,951

**Columns:** 9

**Primary Key:** `product_id`

**Foreign Keys:** none

---

## `olist_sellers_dataset.csv`

**Purpose:** The independent sellers who fulfill orders through the marketplace, and their location.

**Rows:** 3,095

**Columns:** 4

**Primary Key:** `seller_id`

**Foreign Keys:** none

---

## `olist_geolocation_dataset.csv`

**Purpose:** Brazilian zip code prefixes mapped to latitude and longitude, for mapping and distance calculations. The largest table in the dataset.

**Rows:** 1,000,163

**Columns:** 5

**Primary Key:** none (not unique; see Data Quality)

**Foreign Keys:** none formally; joins to customers and sellers by matching zip code prefix

---

## `product_category_name_translation.csv`

**Purpose:** Translates the Portuguese product category names used in products.csv into English.

**Rows:** 71

**Columns:** 2

**Primary Key:** `product_category_name`

**Foreign Keys:** none

---

# Data Dictionary

## `olist_orders_dataset.csv`

| Column | Data Type | Description | Business Meaning |
|---|---|---|---|
| `order_id` | string (PK) | Unique order identifier | Join key |
| `customer_id` | string (FK) | Order-level customer identifier | Links to customers; see Data Quality note on `customer_id` vs `customer_unique_id` |
| `order_status` | string | delivered / shipped / canceled / unavailable / invoiced / processing / created / approved | Only delivered orders have complete delivery timestamps |
| `order_purchase_timestamp` | datetime | When the order was placed | Time series analysis |
| `order_approved_at` | datetime, some missing | When payment was approved | Funnel timing |
| `order_delivered_carrier_date` | datetime, some missing | When the order was handed to the logistics carrier | Fulfillment timing |
| `order_delivered_customer_date` | datetime, some missing | When the customer actually received the order | Actual delivery date, only present for delivered orders |
| `order_estimated_delivery_date` | datetime | The delivery date promised to the customer at purchase | Benchmark for on-time vs late delivery |

---

## `olist_order_items_dataset.csv`

| Column | Data Type | Description | Business Meaning |
|---|---|---|---|
| `order_id` | string (FK) | Which order this item belongs to | Links to orders |
| `order_item_id` | int | Sequence number of this item within the order | Part of composite key |
| `product_id` | string (FK) | Which product | Links to products |
| `seller_id` | string (FK) | Which seller fulfilled this item | Links to sellers |
| `price` | float | Price of this item | Revenue; sum across items for order total |
| `freight_value` | float | Shipping cost allocated to this item | Logistics cost analysis |

---

## `olist_order_payments_dataset.csv`

| Column | Data Type | Description | Business Meaning |
|---|---|---|---|
| `order_id` | string (FK) | Which order this payment applies to | Links to orders |
| `payment_sequential` | int | Sequence number when an order has multiple payments | Part of composite key |
| `payment_type` | string | credit_card / boleto / voucher / debit_card / not_defined | Payment method analysis |
| `payment_installments` | int | Number of installments chosen | Financing behavior |
| `payment_value` | float | Amount paid in this payment record | Revenue; sum across records for order total |

---

## `olist_order_reviews_dataset.csv`

| Column | Data Type | Description | Business Meaning |
|---|---|---|---|
| `review_id` | string (PK) | Unique review identifier | Join key |
| `order_id` | string (FK) | Which order this review is for | Links to orders |
| `review_score` | int, 1 to 5 | Star rating given by the customer | Primary satisfaction metric |
| `review_comment_title` | string, mostly missing | Optional short title | Most reviews have no title (about 88 percent missing) |
| `review_comment_message` | string, often missing | Optional written comment | About 58 percent missing; present reviews may support optional text analysis |
| `review_creation_date` | date | When the review survey was sent | Timing analysis |
| `review_answer_timestamp` | datetime | When the customer submitted the review | Response time analysis |

---

## `olist_customers_dataset.csv`

| Column | Data Type | Description | Business Meaning |
|---|---|---|---|
| `customer_id` | string (PK) | Order-level customer identifier, unique per order | Do not use this to count unique customers; see `customer_unique_id` |
| `customer_unique_id` | string | Person-level identifier, shared across that person’s repeat orders | Use this to identify true repeat customers |
| `customer_zip_code_prefix` | int | First digits of the customer’s zip code | Joins to geolocation (not a strict one-to-one key) |
| `customer_city` | string | Customer’s city | Geographic analysis |
| `customer_state` | string | Customer’s state (two-letter code) | Geographic analysis |

---

## `olist_products_dataset.csv`

| Column | Data Type | Description | Business Meaning |
|---|---|---|---|
| `product_id` | string (PK) | Unique product identifier | Join key |
| `product_category_name` | string, about 610 missing | Category name in Portuguese | Join to category_translation for English name |
| `product_name_lenght` | float, about 610 missing | Character length of the product name (spelling as published) | Listing quality proxy |
| `product_description_lenght` | float, about 610 missing | Character length of the product description | Listing quality proxy |
| `product_photos_qty` | float, about 610 missing | Number of photos in the listing | Listing quality proxy |
| `product_weight_g` | float, a couple missing | Product weight in grams | Freight cost analysis |
| `product_length_cm` / `product_height_cm` / `product_width_cm` | float, a couple missing | Product dimensions in centimeters | Freight cost analysis |

---

## `olist_sellers_dataset.csv`

| Column | Data Type | Description | Business Meaning |
|---|---|---|---|
| `seller_id` | string (PK) | Unique seller identifier | Join key |
| `seller_zip_code_prefix` | int | First digits of seller’s zip code | Joins to geolocation (not a strict one-to-one key) |
| `seller_city` | string | Seller’s city | Geographic analysis |
| `seller_state` | string | Seller’s state | Geographic analysis; sellers are heavily concentrated in a few states |

---

## `olist_geolocation_dataset.csv`

| Column | Data Type | Description | Business Meaning |
|---|---|---|---|
| `geolocation_zip_code_prefix` | int | Zip code prefix | Join key, but not unique; see Data Quality |
| `geolocation_lat` | float | Latitude | Mapping and distance calculations |
| `geolocation_lng` | float | Longitude | Mapping and distance calculations |
| `geolocation_city` | string | City name as recorded for this reading | Geographic analysis |
| `geolocation_state` | string | State as recorded for this reading | Geographic analysis |

---

## `product_category_name_translation.csv`

| Column | Data Type | Description | Business Meaning |
|---|---|---|---|
| `product_category_name` | string (PK) | Category name in Portuguese | Join key back to products |
| `product_category_name_english` | string | Category name in English | Use this for readable category labels |

---

## Important Fields to Use Carefully

`customer_id` is unique per order, not per person, so counting distinct `customer_id` values will overstate unique customers; use `customer_unique_id` for anything about repeat behavior.

There is no target or label column; nothing is meant to be predicted.

---

# Data Relationships

- Every orders row links to exactly one customers row (`customer_id`).
- An order can have multiple `order_items` rows (one per item; about 14 percent of orders have more than one item), each linking to one product and one seller.
- An order can have multiple `order_payments` rows (about 4,400 orders have more than one payment record); sum `payment_value` across an order’s rows to get the total amount paid.
- An order can have zero or more `order_reviews` rows; in practice almost every order has exactly one review record in this dataset.
- Products join to `category_translation` on `product_category_name` to get an English category label.
- Customers and sellers both join to geolocation by matching zip code prefix, but this is not a clean one-to-one join: the geolocation table has roughly 52 rows on average for every unique zip code prefix, reflecting multiple recorded lat/lng readings for the same prefix. Aggregating (for example, taking the mean latitude and longitude per prefix) before joining is a reasonable and common approach.

## Relationship Map

```text
customers -> orders -> order_items -> products -> category_translation
order_items -> sellers
orders -> order_payments
orders -> order_reviews
customers / sellers -> geolocation (matched by zip code prefix, not a strict foreign key)
```

---

# Data Quality Notes

Unlike a synthetic dataset, these are genuine characteristics of real operational data, not issues inserted for the exercise. They are exactly the kind of thing a working analyst has to notice and handle:

- **`order_status` is not always delivered:** 96,478 of 99,441 orders are delivered; the remainder are shipped, canceled, unavailable, invoiced, processing, created, or approved, and most of these lack complete delivery timestamps by nature. Decide deliberately how to treat non-delivered orders in any delivery-time analysis.
- **Missing timestamps:** `order_approved_at` is missing for 160 orders, `order_delivered_carrier_date` for 1,783 orders, and `order_delivered_customer_date` for 2,965 orders, consistent with orders that never completed the normal fulfillment flow.
- **`customer_id` versus `customer_unique_id`:** `customer_id` is unique per order (99,441 unique values, one per order); `customer_unique_id` identifies the same person across multiple orders and has only 96,096 unique values, meaning several thousand people placed more than one order. This distinction is easy to miss and directly affects any repeat-customer analysis.
- **Multi-item and multi-payment orders:** 13,984 orders have more than one `order_items` row, and 4,446 orders have more than one `order_payments` row. Naive row counts on these tables will not equal the number of orders; aggregate deliberately.
- **Missing product information:** 610 products are missing category name and related listing detail fields, and 2 products are missing weight and dimension fields.
- **Mostly-empty review text:** 88,285 of 100,000 reviews have no comment title, and 58,247 have no comment message. Most customers rate without writing anything; text-based analysis is optional and will only apply to a minority of reviews.
- **Geolocation is not a clean lookup table:** 1,000,163 rows cover roughly 19,000 unique zip code prefixes, so joining directly without aggregating first will multiply rows unexpectedly.
- **No injected issues:** there are no artificially inserted duplicates, sign errors, or missing-value patterns in this dataset. Every quirk described here is a real characteristic of the original Olist export.

---

# A Note on Using This Dataset

Because this is real data rather than a dataset built around a predetermined story, the organizer does not have a hidden answer key. The Core Questions above are analytical directions grounded in the dataset’s actual structure and known characteristics, not a preview of specific findings. Two teams can legitimately reach different, well-evidenced conclusions from this data, and both can be excellent submissions. Judges should evaluate the quality of reasoning and evidence, not whether a team’s conclusion matches any single expected answer.

---

# Submission Notes Shared by the Organizer

## Project Submission

https://gradientlearnings.org/events/data-analytics-hackathon/feedback

## LinkedIn Post Submission Form

https://forms.gle/k3cmLhmW2chJPAK7A

## Deadline

**06 September 2026, 11:59 PM IST**

## Important Submission Instructions

1. Make sure the video is uploaded to Google Drive, and the link you submit is publicly accessible, not private.
2. Make sure the Google Colab link is also set to public access.
3. If you get the error **“Invalid input: expected array, received undefined,”** click on **“Add Other Team Members”** and fill in your details as well.

