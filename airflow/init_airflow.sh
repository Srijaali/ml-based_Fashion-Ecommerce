#!/bin/bash

# Initialize Airflow database and create admin user
# This script should be run once to set up the Airflow environment

echo "Initializing Airflow database..."
airflow db init

echo "Creating admin user..."
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com

echo "Creating default connections..."
# Create a default postgres connection
airflow connections add 'postgres_default' \
    --conn-type 'postgres' \
    --conn-host 'localhost' \
    --conn-schema 'ecommerce' \
    --conn-login 'airflow' \
    --conn-password 'airflow' \
    --conn-port 5432

echo "Airflow initialization complete!"
echo "You can now start the webserver with: airflow webserver --port 8080"
echo "And the scheduler with: airflow scheduler"