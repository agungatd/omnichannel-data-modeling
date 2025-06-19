# shopsphere/utils/constants.py

"""
Central location for all constants used across the Shopsphere data pipelines.
This includes table names, paths, and Spark application configurations.
"""
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()



# --- Data Lake Paths (Example for S3) ---
# It's a best practice to externalize these, e.g., in Airflow Variables.
LAKE_BASE_PATH = "s3a://shopsphere-datalake"

# --- Bronze Layer Tables ---
BRONZE_POSTGRES_ORDERS_TABLE = "bronze.postgres_orders"
BRONZE_MONGO_MARKETPLACE_TABLE = "bronze.mongo_marketplace_orders"
BRONZE_KAFKA_EVENTS_TABLE = "bronze.kafka_events"

# --- Silver Layer Tables ---
SILVER_ORDERS_UNIFIED_TABLE = "silver.orders_unified"
SILVER_IDENTITY_GRAPH_TABLE = "silver.identity_graph"
SILVER_USERS_CLEANSED_TABLE = "silver.users_cleansed"

# --- Gold Layer Tables ---
GOLD_DIM_USERS_TABLE = "gold.dim_users"
GOLD_DIM_PRODUCTS_TABLE = "gold.dim_products"
GOLD_DIM_STORES_TABLE = "gold.dim_stores"
GOLD_FACT_ORDERS_TABLE = "gold.fact_orders"
GOLD_USER_RISK_SCORES_TABLE = "gold.user_risk_scores"

# --- Spark Configurations ---
SPARK_JOBS_FILE = "/opt/airflow/dags/shopsphere/utils/spark_jobs.py"
SPARK_CONN_ID = "spark_default"

# --- Source System Details ---
# These would be fetched from Airflow Connections in a real scenario
POSTGRES_CONN_ID = "postgres_shopsphere"
MONGO_CONN_ID = "mongo_shopsphere"

KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
KAFKA_EVENTS_TOPIC = "shopsphere.events"
