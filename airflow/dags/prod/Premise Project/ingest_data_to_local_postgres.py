#yaml
import yaml

# Import required Python standard libraries
import os                  # For handling operating system related functionality
import logging            # For logging
import gzip              # For handling gzip compressed files
import shutil            # For file operations

# Import Airflow related libraries
from airflow import DAG                    # Import DAG class for workflow creation
from airflow.utils.dates import days_ago   # For date handling

# Import Airflow operators
from airflow.operators.bash import BashOperator        # For executing bash commands
from airflow.operators.python import PythonOperator    # For executing Python functions

import pandas as pd
import time
from sqlalchemy import create_engine
import os 


#load config
def load_config():
    config_path = '/opt/airflow/configs/prod.yml'
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
config = load_config()

postgres_host = config['local_postgres']['host']


# Define dataset-related variables
dataset_file = "yellow_tripdata_2021-01.csv"             
dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"   

path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")


def download_and_extract_gz(src_gz_file, dest_csv_file):
    """Decompress .gz file to CSV file
    """
    with gzip.open(src_gz_file, 'rb') as f_in:
        with open(dest_csv_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def ingest_data_to_local_postgres(user, password, host, port, db, table_name, csv_path, **context):
    # Using Airflow task instance logger
    task_instance = context['task_instance']
    task_instance.log.info(f"Attempting to connect to PostgreSQL database: host={host}, port={port}, db={db}, user={user}")
    
    try:
        engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
        with engine.connect() as connection:
            # 首先检查表是否存在
            table_exists = connection.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                )
            """, (table_name,)).scalar()
            
            if table_exists:
                # 如果表存在，检查并清理现有数据
                result = connection.execute(f"SELECT COUNT(*) FROM {table_name}")
                existing_rows = result.scalar()
                
                if existing_rows > 0:
                    task_instance.log.info(f"Found {existing_rows} existing rows in table {table_name}, will overwrite")
                    connection.execute(f"TRUNCATE TABLE {table_name}")
                    task_instance.log.info(f"Table {table_name} has been truncated")
            else:
                task_instance.log.info(f"Table {table_name} does not exist yet, will be created during import")
            
            task_instance.log.info("Successfully connected to PostgreSQL database, starting data import")
    except Exception as e:
        task_instance.log.error(f"Failed to connect to PostgreSQL database: {str(e)}")
        raise

    try:
        df_iterator = pd.read_csv(csv_path, iterator=True, chunksize=100000)
        
        chunk_count = 0
        max_chunks = 3  # only insert max. 300000 rows
        
        try:
            while chunk_count < max_chunks:
                start_time = time.time()    
                df = next(df_iterator)
                df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
                df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
                df.to_sql(name=table_name, con=engine, if_exists='append')
                end_time = time.time()
                task_instance.log.info(f'Inserted new chunk, time taken: {end_time-start_time:.2f} seconds')
                chunk_count += 1
            task_instance.log.info(f"Completed importing {chunk_count * 100000} rows")
        except StopIteration:
            task_instance.log.info("All data has been read (less than 300,000 rows)")
    except Exception as e:
        task_instance.log.error(f"Data import failed: {str(e)}")
        raise

# Set default arguments for the DAG
default_args = {
    "owner": "airflow",                # DAG owner
    "start_date": days_ago(1),         # Start date is 1 day ago
    "depends_on_past": False,          # No dependency on past executions
    "retries": 1,                      # Retry once if failed
}

# Create DAG using context manager
with DAG(
    dag_id="data_ingestion_premise_postgres_dag",    # Unique identifier for the DAG
    schedule_interval="@daily",          # Set to run daily
    default_args=default_args,           # Use default arguments defined above
    catchup=False,                       # Don't execute historical tasks
    max_active_runs=1,                   # Maximum number of concurrent DAG runs
    tags=['premise-postgres-de'],        # DAG tags
) as dag:

    # Define task to download dataset
    download_dataset_task = BashOperator(
        task_id="download_dataset_task",   
        bash_command=f"curl -sS -L --fail {dataset_url} > {path_to_local_home}/{dataset_file}.gz"    # Use curl to download dataset
    )

    # Define task to extract gz file
    extract_gz_task = PythonOperator(
        task_id="extract_gz_task",          # Unique identifier for the task
        python_callable=download_and_extract_gz,    # Python function to call
        op_kwargs={                         # Arguments to pass to the function
            "src_gz_file": f"{path_to_local_home}/{dataset_file}.gz",
            "dest_csv_file": f"{path_to_local_home}/{dataset_file}",
        },
    )

    ingest_data_to_local_postgres_task = PythonOperator(
        task_id="ingest_data_to_local_postgres_task",
        python_callable=ingest_data_to_local_postgres,
        provide_context=True,  # Add this line to provide context
        op_kwargs={
            "user": "airflow",
            "password": "airflow",
            "host": postgres_host,
            "port": "5432",
            "db": "airflow",
            "table_name": "yellow_taxi_trips",
            "csv_path": f"{path_to_local_home}/{dataset_file}",
        },
    )

    download_dataset_task >> extract_gz_task >> ingest_data_to_local_postgres_task