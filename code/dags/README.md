ShopSphere Data Platform DAGs
This directory contains the Airflow DAGs responsible for orchestrating the ETL/ELT pipelines for the ShopSphere omnichannel data platform.

DAG Architecture
The pipeline is managed by three distinct but interconnected DAGs, following the Medallion architecture:

shopsphere_bronze_layer:

Responsibility: Ingests raw data from source systems (PostgreSQL, MongoDB) and streams (Kafka) into the Bronze layer of the data lake.

Schedule: Runs on a schedule (e.g., hourly).

Trigger: On successful completion, it triggers the shopsphere_silver_layer DAG.

shopsphere_silver_layer:

Responsibility: Takes raw data from the Bronze layer and applies cleaning, deduplication, and identity resolution logic to create conformed, queryable tables in the Silver layer.

Schedule: Triggered by the Bronze DAG. Not scheduled to run independently.

Trigger: On successful completion, it triggers the shopsphere_gold_layer DAG.

shopsphere_gold_layer:

Responsibility: Builds the final business-level aggregate tables and dimensional models in the Gold layer. This layer directly serves analytics dashboards and BI tools.

Schedule: Triggered by the Silver DAG.

Setup & Configuration
Airflow Connections: Ensure you have configured the following Airflow connections:

spark_default: A connection to your Spark cluster (e.g., pointing to a Spark Master, Livy, or Databricks).

postgres_shopsphere: JDBC connection details for the source PostgreSQL database.

mongo_shopsphere: Connection details for the source MongoDB database.

Spark Jobs: The actual data transformation logic is written in PySpark and is located in shopsphere/utils/spark_jobs.py. The DAGs use the SparkSubmitOperator to execute these jobs. This separation of concerns makes the code easier to test and maintain.

Constants: All table names, file paths, and application names are defined in shopsphere/utils/constants.py to ensure consistency across all scripts.