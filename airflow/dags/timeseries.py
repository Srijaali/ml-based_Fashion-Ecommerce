"""
DAG D - Time Series Dataset (Dataset D)
Schedule: Daily @ 05:00
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.dummy import DummyOperator

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
    'timeseries',
    default_args=default_args,
    description='ETL pipeline for time series dataset (Dataset D)',
    schedule_interval='0 5 * * *',  # Daily at 05:00
    catchup=False,
    tags=['ml', 'etl', 'dataset-d', 'timeseries'],
)

# Dummy start task
start = DummyOperator(task_id='start', dag=dag)

# Task 1: Extract raw daily series
extract_timeseries_sql = """
-- Extract raw daily series per article and per category from transactions (incremental)
SELECT 
    t.article_id,
    a.index_group_name as category,
    t.t_dat as date,
    COUNT(*) as transaction_count,
    SUM(t.price) as total_sales,
    COUNT(DISTINCT t.customer_id) as unique_customers
FROM transactions t
JOIN articles a ON t.article_id = a.article_id
WHERE t.t_dat >= CURRENT_DATE - INTERVAL '1 day'  -- Incremental extract
GROUP BY t.article_id, a.index_group_name, t.t_dat
ORDER BY t.article_id, a.index_group_name, t.t_dat;
"""

extract_task = PostgresOperator(
    task_id='extract_raw_daily_series',
    postgres_conn_id='postgres_default',
    sql=extract_timeseries_sql,
    dag=dag,
)

# Task 2: Fill gaps & impute
def fill_gaps_impute(**kwargs):
    """Ensure continuous date range, fill missing days as zero sales"""
    print("Filling gaps and imputing missing values in time series")
    # Actual implementation would:
    # - Identify missing dates
    # - Fill with zero values for sales metrics
    # - Ensure continuous time series
    
    return "Gaps filled and data imputed"

fill_gaps_task = PythonOperator(
    task_id='fill_gaps_impute',
    python_callable=fill_gaps_impute,
    dag=dag,
)

# Task 3: Compute rolling features
def compute_rolling_features(**kwargs):
    """Compute rolling_7, rolling_30 features"""
    print("Computing rolling window features")
    # Actual implementation would:
    # - Calculate 7-day and 30-day rolling averages
    # - Compute other rolling statistics
    
    return "Rolling features computed"

compute_rolling_task = PythonOperator(
    task_id='compute_rolling_features',
    python_callable=compute_rolling_features,
    dag=dag,
)

# Task 4: Add calendar flags
def add_calendar_flags(**kwargs):
    """Add holiday, promo flags (if promotion calendar available)"""
    print("Adding calendar flags to time series data")
    # Actual implementation would:
    # - Join with holiday calendar
    # - Add promotional flags
    # - Add day of week, month, etc.
    
    return "Calendar flags added"

add_calendar_task = PythonOperator(
    task_id='add_calendar_flags',
    python_callable=add_calendar_flags,
    dag=dag,
)

# Task 5: Save artifacts
def save_artifacts(**kwargs):
    """Save daily/weekly parquet artifacts"""
    from datetime import datetime
    import os
    
    date_str = datetime.now().strftime("%Y%m%d")
    path = f"data/ml/D_timeseries/{date_str}/"
    os.makedirs(path, exist_ok=True)
    
    print(f"Saving time series artifacts to {path}")
    # Actual implementation would save Parquet files
    
    return f"Artifacts saved to {path}"

save_artifacts_task = PythonOperator(
    task_id='save_artifacts',
    python_callable=save_artifacts,
    dag=dag,
)

# Task 6: Register metadata
def register_metadata(**kwargs):
    """Register metadata"""
    print("Registering metadata for time series dataset")
    # Actual implementation would insert a record into etl_runs table
    
    return "Metadata registered"

register_metadata_task = PythonOperator(
    task_id='register_metadata',
    python_callable=register_metadata,
    dag=dag,
)

# Dummy end task
end = DummyOperator(task_id='end', dag=dag)

# Set task dependencies
start >> extract_task >> fill_gaps_task >> compute_rolling_task >> add_calendar_task >> save_artifacts_task >> register_metadata_task >> end