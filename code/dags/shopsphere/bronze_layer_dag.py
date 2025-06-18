# dags/shopsphere/bronze_layer_dag.py

from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

from shopsphere.utils import constants

with DAG(
    dag_id="shopsphere_bronze_layer",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    schedule="0 * * * *",  # Run hourly
    tags=["shopsphere", "bronze"],
    doc_md="""
    ### Shopsphere Bronze Layer Pipeline

    This DAG is responsible for ingesting raw data from source systems
    into the Bronze layer of the data lake.
    """,
) as dag:
    # --- Task to ingest data from PostgreSQL ---
    ingest_postgres_orders = SparkSubmitOperator(
        task_id="ingest_postgres_orders",
        application=constants.SPARK_JOBS_FILE,
        conn_id=constants.SPARK_CONN_ID,
        # Pass arguments to the PySpark script
        application_args=[
            "--job-name", "ingest_postgres_to_bronze",
            "--table-name", "orders",
            "--bronze-table", constants.BRONZE_POSTGRES_ORDERS_TABLE,
        ],
        # Add required JDBC driver package
        packages="org.postgresql:postgresql:42.6.0",
    )

    # --- Task to ingest data from MongoDB ---
    ingest_mongo_marketplace = SparkSubmitOperator(
        task_id="ingest_mongo_marketplace",
        application=constants.SPARK_JOBS_FILE,
        conn_id=constants.SPARK_CONN_ID,
        application_args=[
            "--job-name", "ingest_mongo_to_bronze",
            "--collection-name", "marketplace_orders",
            "--bronze-table", constants.BRONZE_MONGO_MARKETPLACE_TABLE,
        ],
        # Add required MongoDB Spark Connector package
        packages="org.mongodb.spark:mongo-spark-connector_2.12:10.2.1",
    )
    
    # --- Task to trigger the next DAG in the pipeline ---
    trigger_silver_layer = TriggerDagRunOperator(
        task_id="trigger_silver_layer",
        trigger_dag_id="shopsphere_silver_layer",  # The ID of the DAG to trigger
        # Pass configuration to the next DAG if needed, e.g., the run_id
        conf={"logical_date": "{{ ds }}"},
    )

    # --- Define Task Dependencies ---
    [ingest_postgres_orders, ingest_mongo_marketplace] >> trigger_silver_layer
