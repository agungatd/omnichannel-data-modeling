# dags/shopsphere/silver_layer_dag.py

from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

from shopsphere.utils import constants

with DAG(
    dag_id="shopsphere_silver_layer",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    schedule=None,  # This DAG is only triggered, not scheduled
    tags=["shopsphere", "silver"],
    doc_md="""
    ### Shopsphere Silver Layer Pipeline

    Processes raw data from Bronze to create cleansed, conformed, and deduplicated tables.
    This DAG is triggered by the `shopsphere_bronze_layer` DAG.
    """,
) as dag:
    # --- Task to run identity stitching ---
    run_identity_resolution = SparkSubmitOperator(
        task_id="run_identity_resolution",
        application=constants.SPARK_JOBS_FILE,
        conn_id=constants.SPARK_CONN_ID,
        application_args=["--job-name", "run_identity_resolution"],
    )

    # --- Task to process unified orders ---
    process_unified_orders = SparkSubmitOperator(
        task_id="process_unified_orders",
        application=constants.SPARK_JOBS_FILE,
        conn_id=constants.SPARK_CONN_ID,
        application_args=["--job-name", "process_bronze_to_silver_unified_orders"],
    )

    # --- Task to trigger the Gold layer DAG ---
    trigger_gold_layer = TriggerDagRunOperator(
        task_id="trigger_gold_layer",
        trigger_dag_id="shopsphere_gold_layer",
        conf={"logical_date": "{{ ds }}"},
    )

    # --- Define Task Dependencies ---
    # Identity resolution must run first as its output is needed by other tasks
    run_identity_resolution >> process_unified_orders >> trigger_gold_layer
