Here's your take-home **senior data engineer assignment**, complete with instructions, expectations, example data, and a visual schema.

---

# **Take-Home Assignment: Omnichannel Retail Data Modeling**

## Background:

You’ve just joined **ShopSphere**, a fast-scaling omnichannel retail platform. The company wants a unified data model that integrates online purchases, offline store transactions, third-party marketplaces, and real-time behavioral tracking.

Your mission is to design a **production-ready data model** using lakehouse principles that will support analytics, fraud detection, inventory tracking, and a Customer 360 dashboard.

---

## Assignment Objectives

Your submission should include:

### 1. **Data Model Design**

* **Entity Relationship Diagram (ERD)** or similar logical model
* Clear keys and relationship explanations
* SCD strategy (Type 2)

### 2. **Lakehouse Table Design**

* Partitioning and clustering strategy
* Physical table layout (folder or table design)
* File format decisions (e.g., Parquet + Iceberg)

### 3. **Ingestion Plan**

* Batch for PostgreSQL and MongoDB
* Stream ingestion from Kafka
* Schema evolution handling

### 4. **Data Quality & Governance**

* Identity resolution approach
* Deduplication strategy
* GDPR / historical tracking

### 5. **Sample Data**

Provide sample rows for at least 3 of the following:

* `orders`
* `users`
* `inventory_snapshots`
* `marketplace_orders`
* `events`

### 6. **Design Justification**

Short written rationale (\~1 page max) explaining:

* Tradeoffs in your design
* Choices of format, partitioning, modeling approach
* Assumptions made

---

## Visual Logical Schema (Entity-Level ERD)

```plaintext
                +----------------+
                |     USERS      |
                +----------------+
                | user_id (PK)   |
                | email          |
                | phone_number   |
                | name           |
                | loyalty_id     |
                +----------------+
                         |
                         | 1
                         |        
                         | M
                +----------------+
                |   ORDERS       |
                +----------------+
                | order_id (PK)  |
                | user_id (FK)   |
                | source         |  ← ("web", "pos", "marketplace")
                | created_at     |
                | total_amount   |
                +----------------+
                         |
                         | M
                         |        
                         | 1
                +----------------+
                |  ORDER_ITEMS   |
                +----------------+
                | item_id (PK)   |
                | order_id (FK)  |
                | product_id     |
                | quantity       |
                | price          |
                +----------------+

                +---------------------------+
                | INVENTORY_SNAPSHOTS       |
                +---------------------------+
                | store_id                  |
                | product_id                |
                | snapshot_time             |
                | stock_qty                 |
                +---------------------------+

                +---------------------------+
                |  EVENTS (Kafka)           |
                +---------------------------+
                | event_id                  |
                | user_id                   |
                | timestamp                 |
                | event_type                | ← click, view, add_to_cart
                | metadata (JSON)           |
                +---------------------------+

                +---------------------------+
                |  MARKETPLACE_ORDERS       |
                +---------------------------+
                | mp_order_id               |
                | user_email                |
                | platform                  |
                | product_name              |
                | order_time                |
                | amount                    |
                +---------------------------+
```

---

## Bonus (optional)

* Design a **risk scoring logic** using event + order data
* Create Iceberg DDLs or SQL DDLs for critical tables
* Identity stitching logic (e.g., combine same person across marketplace/email/loyalty)

---

## Submission Format

* ZIP file or GitHub repo

  * `README.md`
  * `schema/` (ERD diagrams, DDLs)
  * `sample_data/`
  * `design_doc.pdf` or `.md`
* Prefer diagrams in PNG, Lucidchart, or Mermaid format

---
