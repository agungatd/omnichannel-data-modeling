# Data Ingestion and Processing Plan

## 1. Batch Ingestion (PostgreSQL & MongoDB)

* **Orchestration**: An Apache Airflow DAG will run on a schedule (e.g., hourly).
* **Tooling**: Apache Spark running on a managed cluster (e.g., AWS Glue, Databricks).
* **Process**:
    1.  **Extraction**: The Spark job reads data from the source systems.
        * **PostgreSQL (Orders, Users)**: Use the Spark JDBC connector. To capture changes efficiently, we will use a watermark (timestamp column like `last_updated_at`) to only pull new or updated records since the last run. For deleted records, a Change Data Capture (CDC) tool like **Debezium** streaming to Kafka is the gold standard. If CDC is not feasible, a nightly full table comparison would be a less efficient alternative.
        * **MongoDB (Marketplace Orders)**: Use the official Spark-MongoDB connector. Read data based on the `order_time` field for incremental loads.
    2.  **Loading to Bronze**: The raw data is written directly into the corresponding Bronze layer Iceberg table (e.g., `bronze.postgres_users`). This ensures a complete, raw backup is always available.
    3.  **Triggering Silver Job**: Upon successful completion, the batch DAG triggers the Silver layer processing job.

## 2. Stream Ingestion (Kafka)

* **Tooling**: A long-running Spark Structured Streaming job.
* **Process**:
    1.  **Read from Kafka**: The Spark job continuously reads from the `events` Kafka topic.
    2.  **Minimal Transformation**: It parses the JSON payload, adds ingestion metadata (e.g., `ingestion_timestamp`, Kafka offset), and casts basic data types.
    3.  **Append to Bronze**: The data is appended to the `bronze.kafka_events` Iceberg table in micro-batches (e.g., every 5 minutes). Iceberg's transactional nature ensures that consumers never see partially written files.

## 3. Silver & Gold Layer Processing

* **Trigger**: These jobs are triggered by the successful completion of the Bronze ingestion jobs.
* **Process (Silver)**:
    1.  Read new data from Bronze tables.
    2.  Apply data cleaning rules (e.g., standardize phone numbers, trim whitespace).
    3.  Execute the **Identity Resolution** logic (see [identity resolution](identity_resolution.md)) to assign a `master_user_id` to all user-related records.
    4.  Unify data from different sources into conformed tables (e.g., `silver.orders_unified`).
    5.  Use `MERGE INTO` in the Silver Iceberg tables, which handles inserts, updates, and duplicates efficiently.
* **Process (Gold)**:
    1.  Read from Silver tables.
    2.  Perform lookups to dimension tables to resolve surrogate keys (e.g., `master_user_id` -> `user_key`).
    3.  Build the `fact_orders` table.
    4.  Update dimension tables (e.g., `dim_users` using SCD Type 2 logic).
    5.  `MERGE INTO` the Gold layer tables.

## 4. Schema Evolution

Schema evolution is handled natively by **Apache Iceberg**.
* **Process**: If a source system adds a new column (e.g., `device_type` in the `orders` table), the pipeline will not fail.
    1.  The Bronze ingestion job will fail initially.
    2.  A data engineer adds the new column to the Bronze Iceberg table using a simple `ALTER TABLE ... ADD COLUMN` command. No data rewrite is needed.
    3.  The job is re-run. It will now successfully ingest the data, with the new column being `null` for old records.
    4.  The new column can then be propagated to the Silver and Gold layers as needed.
Alternatively, we could create airflow job to automate this schema evolution steps.