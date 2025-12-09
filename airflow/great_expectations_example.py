"""
Example of integrating Great Expectations with Airflow for data quality validation
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator

# Default DAG arguments
default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'great_expectations_example',
    default_args=default_args,
    description='Example of integrating Great Expectations with Airflow',
    schedule_interval=None,
    catchup=False,
    tags=['ml', 'data-quality'],
)

# Example of using Great Expectations operator
# This would validate data in a DataFrame or file
ge_validation_task = GreatExpectationsOperator(
    task_id='validate_customer_data',
    data_context_root_dir='/path/to/great_expectations',
    expectation_suite_name='customer_warnings',
    data_asset_name='customer_data',
    dag=dag,
)

def dummy_extract_task(**kwargs):
    """Dummy extract task for demonstration"""
    print("Extracting data for validation...")
    return "extraction_complete"

extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=dummy_extract_task,
    dag=dag,
)

# Set dependencies
extract_task >> ge_validation_task