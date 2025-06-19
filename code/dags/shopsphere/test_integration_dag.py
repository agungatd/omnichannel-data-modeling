from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

from shopsphere.utils import constants

with DAG(
    dag_id="test_integration",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    catchup=False,
    tags=["shopsphere", "test", "integration"],
    doc_md="""
    ### Layer Pipeline Integration Test DAG

    This DAG is responsible for testing the integration of the Bronze layer
    with the Iceberg tables in MinIO. It simulates the ingestion of data
    """,
) as dag:
    
    spark_iceberg_minio_integration = SparkSubmitOperator(
        task_id="spark_iceberg_minio_integration",
        application=constants.SPARK_JOBS_FILE,
        conn_id=constants.SPARK_CONN_ID,
        # Pass arguments to the PySpark script
        application_args=[
            "--job-name", "test_spark_iceberg_minio",
        ],
    )

    spark_iceberg_minio_integration