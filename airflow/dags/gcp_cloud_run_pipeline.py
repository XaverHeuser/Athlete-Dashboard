from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.providers.google.cloud.operators.cloud_run import CloudRunExecuteJobOperator

# Fetch infrastructure variables dynamically from the environment (.env)
GCP_PROJECT = os.environ.get('GCP_PROJECT_ID')
GCP_REGION = os.environ.get('GCP_REGION', 'europe-west1')
JOB_EXTRACT = os.environ.get('CLOUD_RUN_EL_JOB_NAME', 'extract-load-job')
JOB_DBT = os.environ.get('CLOUD_RUN_DBT_JOB_NAME', 'dbt-transform-job')

default_args = {
    'owner': 'data-engineering',
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    dag_id='1_gcp_cloud_run_pipeline',
    default_args=default_args,
    description='Orchestrates Extract-Load and dbt via Cloud Run Jobs',
    schedule=None,
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=['gcp', 'production'],
) as dag:

    # Task 1: Trigger Extract-Load container
    trigger_extract_load = CloudRunExecuteJobOperator(
        task_id='run_extract_load',
        project_id=GCP_PROJECT,
        region=GCP_REGION,
        job_name=JOB_EXTRACT,
        deferrable=True,
    )

    # Task 2: Trigger dbt transform container
    trigger_dbt_transform = CloudRunExecuteJobOperator(
        task_id='run_dbt_transform',
        project_id=GCP_PROJECT,
        region=GCP_REGION,
        job_name=JOB_DBT,
        deferrable=True,
    )

    # Set execution sequence
    trigger_extract_load >> trigger_dbt_transform