"""
DAG B - Articles Content (Dataset B)
Schedule: Daily @ 03:00
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.models import Variable

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
    'articles_content',
    default_args=default_args,
    description='ETL pipeline for articles content dataset (Dataset B)',
    schedule_interval='0 3 * * *',  # Daily at 03:00
    catchup=False,
    tags=['ml', 'etl', 'dataset-b'],
)

# Dummy start task
start = DummyOperator(task_id='start', dag=dag)

# Task 1: Extract structured data
extract_sql = """
-- Pull article metadata and category hierarchy from DB
SELECT 
    a.article_id,
    a.product_code,
    a.prod_name,
    a.product_type_no,
    a.product_type_name,
    a.product_group_name,
    a.graphical_appearance_no,
    a.graphical_appearance_name,
    a.colour_group_code,
    a.colour_group_name,
    a.perceived_colour_value_id,
    a.perceived_colour_value_name,
    a.perceived_colour_master_id,
    a.perceived_colour_master_name,
    a.department_no,
    a.department_name,
    a.index_code,
    a.index_name,
    a.index_group_no,
    a.index_group_name,
    a.section_no,
    a.section_name,
    a.garment_group_no,
    a.garment_group_name,
    a.detail_desc,
    a.price
FROM articles a
ORDER BY a.article_id;
"""

extract_task = PostgresOperator(
    task_id='extract_articles_structured',
    postgres_conn_id='postgres_default',
    sql=extract_sql,
    dag=dag,
)

# Task 2: Validate data
def validate_articles_data(**kwargs):
    """Ensure no missing article_id, price non-negative, category integrity"""
    # Placeholder for validation logic
    print("Validating articles data")
    # Example checks:
    # - No missing article_id
    # - Price non-negative
    # - Category integrity
    
    return "Validation completed"

validate_task = PythonOperator(
    task_id='validate_articles_data',
    python_callable=validate_articles_data,
    dag=dag,
)

# Task 3: Normalize numeric values
def normalize_numeric_values(**kwargs):
    """Compute normalized_price, normalized_stock"""
    # Placeholder for normalization logic
    print("Normalizing numeric values")
    # Example:
    # df['normalized_price'] = (df['price'] - df['price'].min()) / (df['price'].max() - df['price'].min())
    
    return "Normalization completed"

normalize_task = PythonOperator(
    task_id='normalize_numeric_values',
    python_callable=normalize_numeric_values,
    dag=dag,
)

# Task 4: Save structured data
def save_structured_data(**kwargs):
    """Save parquet to data/ml/B_articles_structured/<date>/"""
    from datetime import datetime
    import os
    
    date_str = datetime.now().strftime("%Y%m%d")
    path = f"data/ml/B_articles_structured/{date_str}/"
    os.makedirs(path, exist_ok=True)
    
    print(f"Saving structured data to {path}")
    # Actual implementation would save Parquet files
    
    return f"Data saved to {path}"

save_structured_task = PythonOperator(
    task_id='save_structured_data',
    python_callable=save_structured_data,
    dag=dag,
)

# Task 5: Check if product catalog changed significantly
def check_catalog_change(**kwargs):
    """Check if product catalog changed significantly"""
    # Placeholder for catalog change detection
    print("Checking for significant catalog changes")
    # Example logic:
    # - Compare row counts with previous run
    # - Check for new articles percentage
    
    # Simulate decision: if change > threshold, trigger embeddings DAG
    significant_change = True  # This would be determined dynamically
    
    if significant_change:
        return 'trigger_embeddings_dag'
    else:
        return 'skip_embeddings'

check_catalog_task = BranchPythonOperator(
    task_id='check_catalog_change',
    python_callable=check_catalog_change,
    dag=dag,
)

# Task 6: Trigger embeddings DAG
trigger_embeddings = DummyOperator(
    task_id='trigger_embeddings_dag',
    dag=dag,
)

# Task 7: Skip embeddings DAG
skip_embeddings = DummyOperator(
    task_id='skip_embeddings',
    dag=dag,
)

# Task 8: Register metadata
def register_metadata(**kwargs):
    """Register metadata and notify"""
    print("Registering metadata for articles content dataset")
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
start >> extract_task >> validate_task >> normalize_task >> save_structured_task >> check_catalog_task
check_catalog_task >> trigger_embeddings >> register_metadata_task >> end
check_catalog_task >> skip_embeddings >> register_metadata_task