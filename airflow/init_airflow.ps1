# Initialize Airflow database and create admin user
# This script should be run once to set up the Airflow environment

Write-Host "Initializing Airflow database..."
airflow db init

Write-Host "Creating admin user..."
airflow users create `
    --username admin `
    --firstname Admin `
    --lastname User `
    --role Admin `
    --email admin@example.com

Write-Host "Creating default connections..."
# Create a default postgres connection
airflow connections add 'postgres_default' `
    --conn-type 'postgres' `
    --conn-host 'localhost' `
    --conn-schema 'ecommerce' `
    --conn-login 'airflow' `
    --conn-password 'airflow' `
    --conn-port 5432

Write-Host "Airflow initialization complete!"
Write-Host "You can now start the webserver with: airflow webserver --port 8080"
Write-Host "And the scheduler with: airflow scheduler"