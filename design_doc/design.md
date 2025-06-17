# Design Document: ShopSphere Omnichannel Data Platform

## 1. Introduction and Goals

The primary goal is to build "single source of truth" that is reliable, scalable, and serve multiple use cases:

1. **Business Analytics and Customer 360**: Provide holistic view of customers and their interactions accross all channels.
2. **Real-time Inventory Tracking**: Maintain accurate, near real-time stock levels.
3. **Fraud Detection**: Identify and flag suspicious activities in real-time, probably feeding cleaned and transformed data into a Machine Learning model for fraud detection.

After this we will refer to each use case with its order number (e.g. for Fraud Detection use `usecase no.3`).

This document outline a Lakehouse architecture that balance performance, cost, and flexibility to meet these goals.

## 2. Data Architecture Design: The Medallion Lakehouse

We will adopt a multi-layered Medallion architecture (Bronze, Silver, Gold) to progressively refine data.

* **Bronze Layer (Raw Data)**:
This layer serve as the initial lending zone for all source data, stored in its original, unaltered format. It provides a historical archive and enable reprocessing if business logic changes.
  * Tables: For table naming format I'll use `<layer>_<source>__<entity>_<name>` such as:
	*  `bronze_postgres__orders`
	*  `bronze_mongo__marketplace_orders`
	*  `bronze_kafka__events`
  * Format: Data is ingested and stored as-is. often in its native format or converted to Parquet for storage and accessibility efficiency if we are using *Iceberg* as the table format. for real-time (write-heavy) data consider to store in Avro format.

* **Silver Layer (Cleansed & Transformed Data)**:
Data from Bronze layer is cleaned, deduplicated, and transformed into queryable data model. This is where the identity resolution occurs and the foundational tables (e.g., clean `users`, unified `orders`) are built.
	* Tables: For table naming format I'll use `<entity>_<name>__<transformations>` such as:
		* `users_scd`
		* `orders_unified`
		* `inventory_snapshots`.
	* Format: All tables are stored as **Apache Iceberg** tables with Parquet file format.

* **Gold Layer (Aggregated & Business-Ready Data)**
This layer contains business-level aggregates and dimensional models optimized for analytics and reporting. The Customer 360 dashboard and other BI tools will query this layer.
	* Tables: For table naming format I'll use `<>_<>` such as:
		* ``
	* Format: **Apache Iceberg** tables, potentially with further performance optimization (e.g. partitioning).

## 3. Data Model Design: Star Schema

For the Gold Layer, we will use **Star Schema**. This model is industry-standard for analyics because it is simple to understand, performant for aggregations, and easily extendable.

* **Fact Table**: `fact_order` the central table containing quantitative measures (e.g., `total_amount`, `quantity`) and foreign keys to dimensional tables.
* **Dimension Tables**: These tables describe the business entities (`dim_users`, `dim_products`, `dim_stores`, `dim_date`). They contain descriptive attributes used for filtering and grouping.

### 3.1. Slowly Changing Dimension

To track historical changes in dimension tables. We will use **SCD Type 2** strategy for `dim_users`. This means instead of overwriting user attribute changes (e.g. address), we will create a new record. Each record will have `is_current` (bool) and `end_date` columns to maintain the full history. This is critical for accurate historical reporting and GDPR compliance.

## 4. Tech & Tools Choice and its Tradeoffs

* **Object Storage (AWS S3/GCS)**:
	* **Choice**: The foundation of lakehouse. because it is highly durable, scalable, and extremely cost-effective compared to traditional HDFS or database storage.
	* **Tradeoff**: Higher latency than attached storage, but this mitigated by our processing engine and table format [read more](./explanations/object-storage.md).

* **Apache Iceberg (Table Format)**:
	* **Choice**: Iceberg is chosen over traditional Hive tables or even Delta Lake for several key reasons:
	  1. **Atomic Transactions & Reliability**: it guarantees data integrity.
	  2. **Schema Evolution**:
	  3. **Time Travel**:
	  4. **Partition Evolution**:
	  5. **Others**: [Iceberg vs Delta lake (2025)](https://bigdataperformance.substack.com/p/delta-lake-vs-apache-iceberg-the)
	* **Tradeoff**: Although it is a relative newer and slightly smaller community than `Delta Lake`, but its feature set is better fit for our governance and schema evolution needs. read more on the link on *Others* reason above.

* **Apache Parquet (File Format)**:
    * **Choice**: The best in class columnar storage format. It offers excellent compression and performance for analytical queries because it allows engine to read only the columns needed.
		* **Tradeoff**: Not optimal for write-heavy, transactional workloads, but that is handled by the source OLTP databases.

* **Apache Avro (File Format)**:
    * **Choice**: This format offers compact binary encoding, fast sequential writes, and strong schema evolution support, making it well-suited for evolving schemas and frequent append (write-heavy) operations
		* **Tradeoff**: used for real-time data only and used only on Bronze layer for fast and efficient data ingestion.

* **Apache Spark (Processing Engine)**:
    * **Choice**: The de-facto standard for large-scale data processing. It has robust integrations with all our chosen technologies (Kafka, Iceberg, Parquet) and can handle both batch and streaming workloads.
    * **Tradeoff**: Can have a steep learning curve and operational overhead if self-managed. Using a managed service like AWS Glue, Databricks, or Google Cloud Dataproc is highly recommended to reduce this overhead.
	
* **Other Considerations**:
	* If the real-time data ingestion is very high in volume and velocity and also need to be cleaned, transformed or enrich for real-time reporting and application. then, we will use *Apache Flink* for data processing before storing it into our bronze table. In parallel the processed data could also be directly write into another kafka topic if it used for another application or service. FLink performed better than spark streaming in real-time data scenario.

## 5. Assumptions & Indonesian Context

* **Cloud Platform**: Assumes a major cloud provider (AWS, GCP, Azure) is used. The architecture should be cloud-agnostic.
* **Data Volume**: The design assumes data volume will grow significantly, making scalability and cost key concerns.
* **Cost-Effectiveness**: In the economic context, managing Total Cost of Ownership (TCO) is paramount. The choice of object storage, Parquet, and the ability to use spot instances for Spark clusters makes this architecture highly cost-efficient.
* **Marketplace Data**: Data from Indonesian marketplaces (e.g., Tokopedia, Shopee) can be inconsistent. The ingestion plan includes a robust cleaning and mapping step to handle variations in `product_name` and user identifiers.
* **Identity**: User identity is fragmented. A user may use an email for a web order, a phone number at a POS, and a different email on a marketplace. Our identity resolution strategy ([see](../scripts/identity_resolution.md)) is a cornerstone of this design.
