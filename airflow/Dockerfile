FROM apache/airflow:2.7.0

# Switch to root to install packages
USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && apt-get clean

# Switch back to airflow user
USER airflow

# Copy requirements file
COPY requirements.txt /opt/airflow/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt

# Create directories
RUN mkdir -p /opt/airflow/data/ml