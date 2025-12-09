"""
DAG E - Reviews NLP Dataset (Dataset E)
Schedule: Nightly @ 01:00
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.dummy import DummyOperator
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator

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
    'reviews_nlp',
    default_args=default_args,
    description='ETL pipeline for reviews NLP dataset (Dataset E)',
    schedule_interval='0 1 * * *',  # Nightly at 01:00
    catchup=False,
    tags=['ml', 'etl', 'nlp', 'dataset-e'],
)

# Dummy start task
start = DummyOperator(task_id='start', dag=dag)

# Task 1: Extract reviews
extract_reviews_sql = """
-- Extract reviews joined with article category
SELECT 
    r.review_id,
    r.customer_id,
    r.article_id,
    a.index_group_name as category,
    r.review_text,
    r.rating,
    r.review_date
FROM reviews r
JOIN articles a ON r.article_id = a.article_id
ORDER BY r.review_date DESC;
"""

extract_task = PostgresOperator(
    task_id='extract_reviews',
    postgres_conn_id='postgres_default',
    sql=extract_reviews_sql,
    dag=dag,
)

# Task 2: Text cleaning
def text_cleaning(**kwargs):
    """Remove URLs, normalize whitespace, lowercase"""
    print("Cleaning review text data")
    # Actual implementation would:
    # - Remove URLs
    # - Normalize whitespace
    # - Convert to lowercase
    # - Other text preprocessing
    
    return "Text cleaning completed"

text_cleaning_task = PythonOperator(
    task_id='text_cleaning',
    python_callable=text_cleaning,
    dag=dag,
)

# Task 3: Quality checks
def quality_checks(**kwargs):
    """Min length, non-empty review_text threshold"""
    print("Running quality checks on reviews data")
    # Actual implementation would check:
    # - Minimum text length
    # - Non-empty reviews
    # - Rating validity (1-5 scale)
    
    return "Quality checks passed"

quality_check_task = PythonOperator(
    task_id='quality_checks',
    python_callable=quality_checks,
    dag=dag,
)

# Task 4: Baseline sentiment (fast CPU)
def baseline_sentiment(**kwargs):
    """VADER or similar for immediate use"""
    print("Computing baseline sentiment scores")
    # Actual implementation would use VADER or similar lightweight sentiment analyzer
    
    return "Baseline sentiment computed"

baseline_sentiment_task = PythonOperator(
    task_id='baseline_sentiment',
    python_callable=baseline_sentiment,
    dag=dag,
)

# Task 5: BERT embeddings (GPU/ML worker DAG)
bert_embedding_task = KubernetesPodOperator(
    task_id='generate_bert_embeddings',
    name='reviews-bert-embeddings',
    namespace='default',
    image='ml-nlp:latest',
    cmds=["python", "generate_review_embeddings.py"],
    env_vars={
        'INPUT_PATH': '/data/reviews',
        'OUTPUT_PATH': '/data/embeddings'
    },
    dag=dag,
)

# Task 6: Save artifacts
def save_artifacts(**kwargs):
    """Save artifacts and register"""
    from datetime import datetime
    import os
    
    date_str = datetime.now().strftime("%Y%m%d")
    path = f"data/ml/E_reviews_nlp/{date_str}/"
    os.makedirs(path, exist_ok=True)
    
    print(f"Saving reviews NLP artifacts to {path}")
    # Actual implementation would save processed data and embeddings
    
    return f"Artifacts saved to {path}"

save_artifacts_task = PythonOperator(
    task_id='save_artifacts',
    python_callable=save_artifacts,
    dag=dag,
)

# Task 7: Register metadata
def register_metadata(**kwargs):
    """Register metadata"""
    print("Registering metadata for reviews NLP dataset")
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
start >> extract_task >> text_cleaning_task >> quality_check_task >> baseline_sentiment_task >> bert_embedding_task >> save_artifacts_task >> register_metadata_task >> end