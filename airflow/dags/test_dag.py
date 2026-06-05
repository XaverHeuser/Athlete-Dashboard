from datetime import datetime
import logging

from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from airflow import DAG


# Basic logging function for PythonTask
def log_hello():
    logging.info('--- Python Operator executed successfully! ---')
    print('This is a standard print statement inside the Python function.')


default_args = {'owner': 'airflow', 'retries': 0}

with DAG(
    dag_id='0_local_test_dag',  # '0_' forces it to the top of your UI list
    default_args=default_args,
    description='A simple DAG to test local Airflow execution',
    schedule=None,  # Manual trigger only
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:
    # Task 1: Run a simple Bash Command
    bash_task = BashOperator(
        task_id='run_bash_command',
        bash_command="echo '--- Bash Operator executed successfully! ---'",
    )

    # Task 2: Run the Python function defined above
    python_task = PythonOperator(
        task_id='run_python_function', python_callable=log_hello
    )

    # Set the execution order: Bash runs first, then Python
    bash_task >> python_task
