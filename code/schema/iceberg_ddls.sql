-- Gold Layer: Dimension Table for Users (SCD Type 2)
CREATE TABLE gold.dim_users (
    user_key BIGINT,
    master_user_id STRING,
    name STRING,
    email STRING,
    phone_number STRING,
    loyalty_id STRING,
    created_date TIMESTAMP,
    is_current BOOLEAN,
    effective_date TIMESTAMP,
    end_date TIMESTAMP,
    last_updated TIMESTAMP
)
USING iceberg
PARTITIONED BY (months(last_updated));

-- Gold Layer: Fact Table for Orders
CREATE TABLE gold.fact_orders (
    order_id STRING,
    user_key BIGINT,
    product_key BIGINT,
    store_key BIGINT,
    order_date_key INT, -- e.g., 20240615
    order_timestamp TIMESTAMP,
    total_amount DECIMAL(18, 2),
    quantity INT,
    source_channel STRING, -- 'web', 'pos', 'marketplace_shopee', 'marketplace_tokopedia'
    ingestion_timestamp TIMESTAMP
)
USING iceberg
PARTITIONED BY (months(order_timestamp), source_channel)
TBLPROPERTIES ('write.distribution-mode'='hash'); -- Optimize for writes

-- Silver Layer: Unified and Cleansed Orders Table
CREATE TABLE silver.orders_unified (
    order_id STRING,
    master_user_id STRING, -- Before being resolved to user_key
    product_id STRING,
    store_id STRING,
    order_timestamp TIMESTAMP,
    total_amount DECIMAL(18, 2),
    quantity INT,
    source_channel STRING,
    raw_payload STRING -- Store original JSON/record for traceability
)
USING iceberg
PARTITIONED BY (days(order_timestamp));

-- Bronze Layer: Raw Kafka Events
CREATE TABLE bronze.kafka_events (
    event_id STRING,
    user_id STRING, -- Can be null or internal ID
    timestamp TIMESTAMP,
    event_type STRING,
    metadata STRING, -- Stored as raw JSON string
    kafka_offset BIGINT,
    kafka_partition INT,
    ingestion_timestamp TIMESTAMP
)
USING iceberg
PARTITIONED BY (days(ingestion_timestamp), event_type);