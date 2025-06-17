# Design Document: ShopSphere Omnichannel Data Platform

## Introduction and Goals

The primary goal is to build "single source of truth" that is reliable, scalable, and serve multiple use cases:

1. **Business Analytics and Customer 360**: Provide holistic view of customers and their interactions accross all channels.
2. **Real-time Inventory Tracking**: Maintain accurate, near real-time stock levels.
3. **Fraud Detection**: Identify and flag suspicious activities in real-time, probably feeding cleaned and transformed data into a Machine Learning model for fraud detection.

After this we will refer to each use case with its order number (e.g. for Fraud Detection use `usecase no.3`).

This document outline a Lakehouse architecture that balance performance, cost, and flexibility to meet these goals.

## Data Architecture Design: The Medallion Lakehouse

We will adopt a multi-layered Medallion architecture (Bronze, Silver, Gold) to progressively refine data.

* **Bronze Layer (Raw Data)**:
This layer serve as the initial lending zone for all source data, stored in its original, unaltered format. It provides a historical archive and enable reprocessing if business logic changes.
  * Tables: For table naming format I'll use `<layer>_<source>__<entity>_<name>` such as:
	*  `bronze_postgres__orders`
	*  `bronze_mongo__marketplace_orders`
	*  `bronze_kafka__events`
  * Format: Data is ingested and stored as-is. often in its native format or converted to Parquet for storage and accessibility efficiency if we are using *Iceberg* as the table format.

* **Silver Layer (Cleansed & Transformed Data)**:
Data from Bronze layer is cleaned, deduplicated, and transformed into queryable data model. This is where the identity resolution occurs and the foundational tables (e.g., clean `users`, unified `orders`) are built.
	* Tables: For table naming format I'll use `<entity>_<name>__<transformations>` such as:
		* `users_scd`
		* `orders_unified`
		* `inventory_snapshots`.
	* Format: All tables are stored as **Apache Iceberg** tables with Parquet file format.

* **Gold Layer (Aggregated & Business-Ready Data)**
This layer contains business-level aggregates and dimensional models optimized for analytics and reporting. The Customer 360 dashboard and other BI tools will query this layer.

## 
