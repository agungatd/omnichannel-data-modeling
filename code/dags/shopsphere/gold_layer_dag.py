# dags/shopsphere/gold_layer_dag.py

from __future__ import annotations

import pendulum

from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

from shopsphere.utils import constants

def final_pipeline_success_log():
    """A simple Python function to log the pipeline completion."""
    print("Shopsphere full ETL pipeline completed successfully!")

with DAG(
    dag_id="shopsphere_gold_layer",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    schedule=None,  # This DAG is also triggered
    tags=["shopsphere", "gold"],
    doc_md="""
    ### Shopsphere Gold Layer Pipeline

    Builds the final business-level aggregate and dimensional models for analytics.
    This DAG is triggered by the `shopsphere_silver_layer` DAG.
    """,
) as dag:
    # --- Task to build all dimension tables ---
    build_dimensions = SparkSubmitOperator(
        task_id="build_dimension_tables",
        application=constants.SPARK_JOBS_FILE,
        conn_id=constants.SPARK_CONN_ID,
        application_args=["--job-name", "build_dimension_tables"],
    )

    # --- Task to build the main fact table. Depends on dimensions being ready. ---
    build_fact_table = SparkSubmitOperator(
        task_id="build_fact_orders",
        application=constants.SPARK_JOBS_FILE,
        conn_id=constants.SPARK_CONN_ID,
        application_args=["--job-name", "build_fact_orders"],
    )

    # --- Task for the bonus requirement: calculating risk scores ---
    calculate_risk_scores_task = SparkSubmitOperator(
        task_id="calculate_risk_scores",
        application=constants.SPARK_JOBS_FILE,
        conn_id=constants.SPARK_CONN_ID,
        application_args=["--job-name", "calculate_risk_scores"],
    )

    # --- Final success logging task ---
    log_completion = PythonOperator(
        task_id="log_pipeline_completion",
        python_callable=final_pipeline_success_log,
    )

    # --- Define Task Dependencies ---
    # Dimensions must be built before facts can be built.
    # Risk scores can be calculated in parallel with building the fact table.
    build_dimensions >> [build_fact_table, calculate_risk_scores_task] >> log_completion
