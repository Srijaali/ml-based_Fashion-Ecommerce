# Airflow ETL Pipeline for ML System

This directory contains Apache Airflow DAGs for orchestrating the ETL pipelines that feed the ML system.

## Directory Structure

```
airflow/
├── dags/                 # Airflow DAGs
├── logs/                 # Airflow logs
├── plugins/              # Custom Airflow plugins
└── requirements.txt      # Python dependencies
```

## DAGs Overview

### Dataset A - User-Item Interactions
- **File**: [dags/user_item_interactions.py](dags/user_item_interactions.py)
- **Schedule**: Daily @ 02:00
- **Purpose**: Recommendation backbone (collaborative filtering & behavioral features)

### Dataset B - Article Content (Structured + Text)
- **File**: [dags/articles_content.py](dags/articles_content.py)
- **Schedule**: Daily @ 03:00
- **Purpose**: Product features, embeddings, similar-product recsys

### Dataset B-Embeddings - Article Embeddings
- **File**: [dags/articles_embeddings.py](dags/articles_embeddings.py)
- **Schedule**: Weekly or on-demand
- **Purpose**: TF-IDF vectors, BERT embeddings, CLIP image embeddings

### Dataset C - Customer Features
- **File**: [dags/customer_features.py](dags/customer_features.py)
- **Schedule**: Daily @ 04:00
- **Purpose**: Segmentation, personalization

### Dataset D - Time-Series Dataset
- **File**: [dags/timeseries.py](dags/timeseries.py)
- **Schedule**: Daily @ 05:00
- **Purpose**: Trending articles, forecasting, seasonality

### Dataset E - Reviews NLP Dataset
- **File**: [dags/reviews_nlp.py](dags/reviews_nlp.py)
- **Schedule**: Nightly @ 01:00
- **Purpose**: Sentiment analysis, embedding search

### Dataset F - Events + Session Funnels
- **File**: [dags/events_and_funnels.py](dags/events_and_funnels.py)
- **Schedule**: Every 15 minutes
- **Purpose**: Behavioral recsys (based on interactions)

## Setup Instructions

1. Install Airflow and dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Initialize the Airflow database:
   ```bash
   airflow db init
   ```

3. Initialize Airflow (this will create the database and admin user):
   
   On Linux/macOS:
   ```bash
   chmod +x init_airflow.sh
   ./init_airflow.sh
   ```
   
   On Windows:
   ```powershell
   .\init_airflow.ps1
   ```

4. Start the Airflow webserver:
   ```bash
   airflow webserver --port 8080
   ```

5. In another terminal, start the Airflow scheduler:
   ```bash
   airflow scheduler
   ```

## Configuration

The initialization script will create the necessary connections. Ensure the following Airflow connections are configured:
- `postgres_default` - Connection to the main database

## Design Principles

- **Idempotent tasks**: All tasks are safe to re-run
- **Small tasks**: DAGs are broken into many well-defined tasks
- **Separation of concerns**: Heavy embedding work is separated from light orchestration
- **Observability**: All DAGs include logging and metadata registration
- **Versioning**: Artifacts are saved with versioned paths

For more information, see [context.md](../context.md) in the project root.