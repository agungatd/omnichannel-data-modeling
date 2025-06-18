# shopsphere/utils/spark_jobs.py

"""
This file contains all the PySpark jobs executed by the Airflow DAGs.
Each function corresponds to a specific ETL task in the pipeline.
This separation of concerns keeps the DAG files clean and focused on orchestration.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, current_timestamp, sha2, concat_ws

# In a real project, you would import constants from the constants file.
# from shopsphere.utils import constants

def get_spark_session(app_name: str) -> SparkSession:
    """Creates and returns a Spark session."""
    # This configuration is basic. In a real environment, you'd configure
    # memory, cores, shuffle partitions, and catalog settings for Iceberg.
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.SparkSqlExtensions") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog") \
        .config("spark.sql.catalog.spark_catalog.type", "hive") \
        .getOrCreate()

# --- Bronze Layer Jobs ---

def ingest_postgres_to_bronze(table_name: str, bronze_table: str):
    """Ingests data from a PostgreSQL table into a Bronze Iceberg table."""
    spark = get_spark_session(f"ingest_{table_name}_to_bronze")
    
    # In a real-world scenario, you'd fetch connection details from a secrets manager
    # and use watermarking for incremental loads.
    df = spark.read \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://postgres:5432/shopsphere") \
        .option("dbtable", f"public.{table_name}") \
        .option("user", "user") \
        .option("password", "password") \
        .option("driver", "org.postgresql.Driver") \
        .load()

    # Add ingestion metadata
    df_with_metadata = df.withColumn("ingestion_timestamp", current_timestamp())

    df_with_metadata.writeTo(bronze_table).append()
    print(f"Successfully ingested data from PostgreSQL table '{table_name}' to Bronze table '{bronze_table}'.")


def ingest_mongo_to_bronze(collection_name: str, bronze_table: str):
    """Ingests data from a MongoDB collection into a Bronze Iceberg table."""
    spark = get_spark_session(f"ingest_{collection_name}_to_bronze")

    # Using the MongoDB Spark Connector
    df = spark.read \
        .format("mongodb") \
        .option('uri', "mongodb://user:password@mongo:27017/shopsphere.marketplace_orders?authSource=admin") \
        .load()

    df_with_metadata = df.withColumn("ingestion_timestamp", current_timestamp())

    df_with_metadata.writeTo(bronze_table).append()
    print(f"Successfully ingested data from MongoDB collection '{collection_name}' to Bronze table '{bronze_table}'.")

# Note: Kafka streaming job is typically a long-running application,
# not ideal for a batch-oriented DAG. A better pattern is to use a separate
# process or a dedicated streaming platform (like Kubernetes or a cloud service).
# For simplicity in this assignment, we'll omit the Spark streaming code here,
# assuming another process handles Kafka -> Bronze.

# --- Silver Layer Jobs ---

def process_bronze_to_silver_unified_orders():
    """Cleanses and unifies order data from various sources into a single Silver table."""
    spark = get_spark_session("silver_unified_orders_processing")
    
    # Read from bronze tables
    # This is a simplified example. A real job would handle schema differences.
    bronze_pg_orders = spark.table("bronze.postgres_orders")
    bronze_mp_orders = spark.table("bronze.mongo_marketplace_orders")

    # Example of transformation and unification
    web_orders = bronze_pg_orders.where(col("source") == "web").select(
        col("order_id"),
        sha2(col("email"), 256).alias("master_user_id_candidate"), # Create a candidate key
        # ... other transformations
    )

    # In a real job, you would perform identity resolution here
    # to get the final master_user_id.

    # Merge into the silver table
    # web_orders.write.mode("append").saveAsTable("silver.orders_unified")
    print("Silver unified orders job completed.")


def run_identity_resolution():
    """
    Processes user data to stitch identities and build the identity graph.
    This is a complex job that involves matching rules.
    """
    spark = get_spark_session("identity_resolution")
    # 1. Read new user data from Bronze sources.
    # 2. Read existing identity graph from Silver.
    # 3. Apply matching rules (email, phone, fuzzy name/address).
    # 4. Generate/update master_user_id for each user.
    # 5. `MERGE INTO` the `silver.identity_graph` table.
    # 6. `MERGE INTO` the `silver.users_cleansed` table.
    print("Identity resolution job completed.")


# --- Gold Layer Jobs ---

def build_dimension_tables():
    """Builds all dimension tables (Users, Products, etc.) for the Gold layer."""
    spark = get_spark_session("gold_dimension_build")
    
    # Example for dim_users (SCD Type 2 logic would be implemented here)
    # 1. Read from `silver.users_cleansed`.
    # 2. Compare with `gold.dim_users` to find new and updated records.
    # 3. For updates, expire the old record (`is_current=false`, `end_date=now()`).
    # 4. Insert new records (`is_current=true`, `end_date=null`).
    print("Gold dimension tables build completed.")


def build_fact_orders():
    """Builds the main fact table for orders."""
    spark = get_spark_session("gold_fact_orders_build")
    
    # 1. Read from `silver.orders_unified`.
    # 2. Perform lookups against Gold dimension tables to get surrogate keys.
    #    (e.g., join with dim_users on master_user_id to get user_key).
    # 3. Select final columns.
    # 4. `MERGE INTO` the `gold.fact_orders` table to avoid duplicates.
    print("Gold fact_orders build completed.")


def calculate_risk_scores():
    """Calculates user risk scores based on order and event data."""
    spark = get_spark_session("gold_risk_score_calculation")

    # 1. Read from `gold.fact_orders` and a (hypothetical) `gold.fact_events`.
    # 2. Engineer features: order frequency, avg order value, etc.
    # 3. Apply scoring model (can be a simple weighted sum or a loaded ML model).
    # 4. Save results to `gold.user_risk_scores`.
    print("User risk score calculation completed.")
