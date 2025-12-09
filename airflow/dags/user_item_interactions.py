"""
DAG A - User-Item Interactions (Dataset A)
Schedule: Daily @ 02:00
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup

# Default DAG arguments
default_args = {
    'owner': 'ml-team',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'user_item_interactions',
    default_args=default_args,
    description='ETL pipeline for user-item interactions dataset (Dataset A)',
    schedule_interval='0 2 * * *',  # Daily at 02:00
    catchup=False,
    tags=['ml', 'etl', 'dataset-a'],
)

# Dummy start task
start = DummyOperator(task_id='start', dag=dag)

# Task 1: Extract from DB
extract_sql = """
-- Canonical SQL query to compute grouped user-item rows
SELECT 
    customer_id,
    article_id,
    COUNT(*) as interaction_count,
    MAX(t_dat) as last_interaction_date
FROM transactions 
GROUP BY customer_id, article_id
ORDER BY customer_id, article_id;
"""

extract_task = PostgresOperator(
    task_id='extract_user_item_interactions',
    postgres_conn_id='postgres_default',
    sql=extract_sql,
    dag=dag,
)

# Task 2: Transform (light)
def transform_user_item_data(**kwargs):
    """Compute recency_days and time_weighted_score"""
    # In a real implementation, this would pull data from the previous task
    # and perform transformations
    import pandas as pd
    from datetime import datetime
    
    # Placeholder for actual transformation logic
    print("Performing light transformations on user-item data")
    # Example transformation:
    # df['recency_days'] = (datetime.now() - df['last_interaction_date']).dt.days
    # df['time_weighted_score'] = df['interaction_count'] / (1 + df['recency_days'] * 0.1)
    
    return "Transformation completed"

transform_task = PythonOperator(
    task_id='transform_user_item_data',
    python_callable=transform_user_item_data,
    dag=dag,
)

# Task 3: Quality check
def quality_check_data(**kwargs):
    """Run schema + min/max checks"""
    # Placeholder for quality checks
    print("Running quality checks on user-item data")
    # Example checks:
    # - No null PKs (customer_id, article_id)
    # - interaction_count > 0
    # - recency_days >= 0
    
    return "Quality checks passed"

quality_check_task = PythonOperator(
    task_id='quality_check_data',
    python_callable=quality_check_data,
    dag=dag,
)

# Task 4: Save artifact
def save_artifact(**kwargs):
    """Write Parquet and CSV to data/ml/A_user_item_interactions/<date>/"""
    # Placeholder for saving artifacts
    from datetime import datetime
    import os
    
    date_str = datetime.now().strftime("%Y%m%d")
    path = f"data/ml/A_user_item_interactions/{date_str}/"
    os.makedirs(path, exist_ok=True)
    
    print(f"Saving artifacts to {path}")
    # Actual implementation would save Parquet and CSV files
    
    return f"Artifacts saved to {path}"

save_artifact_task = PythonOperator(
    task_id='save_artifact',
    python_callable=save_artifact,
    dag=dag,
)

# Task 5: Register metadata
def register_metadata(**kwargs):
    """Record row counts, file paths, min/max dates in metadata table"""
    # Placeholder for metadata registration
    print("Registering metadata for user-item interactions dataset")
    # Actual implementation would insert a record into etl_runs table
    
    return "Metadata registered"

register_metadata_task = PythonOperator(
    task_id='register_metadata',
    python_callable=register_metadata,
    dag=dag,
)

# Task 6: Notify
def send_notification(**kwargs):
    """Send success/failure to Slack"""
    # Placeholder for notification
    print("Sending notification to Slack")
    # Actual implementation would use Slack API
    
    return "Notification sent"

notify_task = PythonOperator(
    task_id='send_notification',
    python_callable=send_notification,
    trigger_rule='all_done',  # Run regardless of upstream success/failure
    dag=dag,
)

# Dummy end task
end = DummyOperator(task_id='end', dag=dag)

# Set task dependencies
start >> extract_task >> transform_task >> quality_check_task >> save_artifact_task >> register_metadata_task >> notify_task >> end