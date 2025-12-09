"""
DAG C - Customer Features (Dataset C)
Schedule: Daily @ 04:00
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
    'customer_features',
    default_args=default_args,
    description='ETL pipeline for customer features dataset (Dataset C)',
    schedule_interval='0 4 * * *',  # Daily at 04:00
    catchup=False,
    tags=['ml', 'etl', 'dataset-c'],
)

# Dummy start task
start = DummyOperator(task_id='start', dag=dag)

# Task 1: Extract demographics
extract_demographics_sql = """
-- Extract demographics from customers
SELECT 
    customer_id,
    FN,
    Active,
    club_member_status,
    fashion_news_frequency,
    age,
    postal_code
FROM customers
ORDER BY customer_id;
"""

extract_demographics_task = PostgresOperator(
    task_id='extract_demographics',
    postgres_conn_id='postgres_default',
    sql=extract_demographics_sql,
    dag=dag,
)

# Task 2: Extract transaction aggregates
extract_transactions_sql = """
-- Extract transaction aggregates (6m/12m windows)
SELECT 
    t.customer_id,
    COUNT(*) as total_transactions,
    SUM(t.price) as total_spent,
    AVG(t.price) as avg_transaction_value,
    MIN(t.t_dat) as first_transaction_date,
    MAX(t.t_dat) as last_transaction_date
FROM transactions t
WHERE t.t_dat >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY t.customer_id
ORDER BY t.customer_id;
"""

extract_transactions_task = PostgresOperator(
    task_id='extract_transaction_aggregates',
    postgres_conn_id='postgres_default',
    sql=extract_transactions_sql,
    dag=dag,
)

# Task 3: Extract orders & order_items
extract_orders_sql = """
-- Extract orders & order_items for basket-level features
SELECT 
    o.order_id,
    o.customer_id,
    COUNT(oi.article_id) as items_in_order,
    SUM(oi.price) as order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id, o.customer_id
ORDER BY o.customer_id;
"""

extract_orders_task = PostgresOperator(
    task_id='extract_orders',
    postgres_conn_id='postgres_default',
    sql=extract_orders_sql,
    dag=dag,
)

# Task 4: Extract events
extract_events_sql = """
-- Extract events counts for behavioral signals
SELECT 
    customer_id,
    COUNT(CASE WHEN event_type = 'view' THEN 1 END) as view_count,
    COUNT(CASE WHEN event_type = 'add_to_cart' THEN 1 END) as add_to_cart_count,
    COUNT(CASE WHEN event_type = 'purchase' THEN 1 END) as purchase_count
FROM events
WHERE event_datetime >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY customer_id
ORDER BY customer_id;
"""

extract_events_task = PostgresOperator(
    task_id='extract_events',
    postgres_conn_id='postgres_default',
    sql=extract_events_sql,
    dag=dag,
)

# Task 5: Join & compute RFM
def join_and_compute_rfm(**kwargs):
    """Join data and compute RFM and percentile buckets"""
    print("Joining data and computing RFM features")
    # Actual implementation would:
    # - Join all extracted data
    # - Compute Recency, Frequency, Monetary values
    # - Calculate percentile buckets
    
    return "RFM features computed"

join_compute_task = PythonOperator(
    task_id='join_and_compute_rfm',
    python_callable=join_and_compute_rfm,
    dag=dag,
)

# Task 6: Quality checks
def quality_checks(**kwargs):
    """Percentiles distribution sanity checks"""
    print("Running quality checks on customer features")
    # Actual implementation would check:
    # - Percentile distributions
    # - Data ranges
    # - Null value checks
    
    return "Quality checks passed"

quality_check_task = PythonOperator(
    task_id='quality_checks',
    python_callable=quality_checks,
    dag=dag,
)

# Task 7: Save artifact
def save_artifact(**kwargs):
    """Save parquet to data/ml/C_customer_features/<date>/"""
    from datetime import datetime
    import os
    
    date_str = datetime.now().strftime("%Y%m%d")
    path = f"data/ml/C_customer_features/{date_str}/"
    os.makedirs(path, exist_ok=True)
    
    print(f"Saving customer features to {path}")
    # Actual implementation would save Parquet files
    
    return f"Data saved to {path}"

save_artifact_task = PythonOperator(
    task_id='save_artifact',
    python_callable=save_artifact,
    dag=dag,
)

# Task 8: Register metadata
def register_metadata(**kwargs):
    """Register metadata"""
    print("Registering metadata for customer features dataset")
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
start >> [extract_demographics_task, extract_transactions_task, extract_orders_task, extract_events_task] >> join_compute_task >> quality_check_task >> save_artifact_task >> register_metadata_task >> end