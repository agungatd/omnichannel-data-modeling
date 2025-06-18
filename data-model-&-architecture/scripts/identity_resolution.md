# Identity Resolution & Governance Strategy

## 1. Objective

To create a single, canonical `master_user_id` for every unique customer, linking their activities across all platforms (web, POS, marketplaces) to build a true Customer 360 view.

## 2. Identity Stitching Strategy

This is a multi-step process run during the Silver layer ETL.

* **Step 1: Create an Identity Graph Table**
    We will create and maintain a table, `silver.identity_graph`, that links all known identifiers to a single `master_user_id`.
    * **Columns**: `identifier_type` (e.g., 'email', 'phone', 'loyalty_id'), `identifier_value`, `master_user_id`, `last_seen_timestamp`.

* **Step 2: Define Stitching Rules (Hierarchy of Trust)**
    We use a rule-based approach to merge identities. The priority is based on the reliability of the identifier:
    1.  **Loyalty ID**: Highest trust. A customer with a loyalty card is well-identified.
    2.  **Verified Email**: A primary key in the `users` table.
    3.  **Verified Phone Number**: A primary key in the `users` table.
    4.  **Marketplace Email**: Less trusted, as it might be a different email.
    5.  **Heuristics**: Combination of `name` and `shipping_address` (requires fuzzy matching).

* **Step 3: Processing Logic**
    For each batch of new data (e.g., a new marketplace order):
    1.  Extract identifiers (e.g., `user_email` from `marketplace_orders`).
    2.  Look up this identifier in the `identity_graph` table.
    3.  **If a match is found**: Assign the existing `master_user_id` to the new record.
    4.  **If no match is found**:
        * Check if other identifiers from the same record (e.g., name, phone) match an existing `master_user_id`. If so, link this new identifier to that existing `master_user_id`.
        * If still no match, generate a **new** `master_user_id` and insert the new identifier into the graph.

## 3. Deduplication Strategy

Deduplication happens at the Silver layer. Using Iceberg's `MERGE INTO` command with a `WHEN NOT MATCHED THEN INSERT` clause, we can insert new records while ignoring duplicates based on a natural key (e.g., `order_id`). This is efficient and guarantees exactly-once processing.

## 4. GDPR & Historical Tracking (Governance)

* **Right to Erasure**: When a user requests data deletion, we will not physically delete their records, as this would corrupt historical sales figures. Instead, we will **anonymize** their personal data (`name`, `email`, `phone_number`, `address`) in the `dim_users` table by replacing it with placeholder values (e.g., 'REDACTED'). A separate, access-controlled log will track these anonymization events for auditing.
* **Right to Access/Portability**: Iceberg's **time travel** feature is perfect for this. We can query the state of a user's data at any given point in time. A simple Spark job can be written to query all tables for a given `master_user_id`, export the results to CSV or JSON, and provide it to the user.
* **Historical Tracking**: The **SCD Type 2** model for `dim_users` provides a full, accurate history of changes to user attributes, which is essential for both compliance and historical analysis.

## 5. Bonus: Fraud/Risk Scoring Logic

We can create a Gold-level aggregate table, `gold.user_risk_scores`, updated daily.

* **Feature Engineering (run in Spark)**:
    * `order_frequency_last_24h`: `COUNT(order_id)` where `order_timestamp` is in the last 24 hours.
    * `avg_order_value_user`: Average `total_amount` for the `master_user_id`.
    * `time_from_account_creation_to_first_purchase`: In minutes. Very short times can be a red flag.
    * `is_new_shipping_address`: Check against historical addresses.
    * `event_velocity`: `COUNT(event_id)` in the 10 minutes prior to an order. High velocity (bot-like activity) is risky.
    * `distinct_ips_last_7d`: Number of distinct IP addresses used.

* **Scoring Logic (Simple Model)**:
    A weighted sum can provide a basic risk score.
    ```
    Risk Score = (w1 * order_frequency_last_24h) +
                 (w2 * (order_total / avg_order_value_user)) +
                 (w3 * (1 / time_from_account_creation_to_first_purchase)) +
                 (w4 * is_new_shipping_address)
    ```
    This score can then be used to flag orders for manual review. For a more advanced solution, these features would be fed into a trained machine learning model (e.g., XGBoost).