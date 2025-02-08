# 这是主要的DAG文件，用于数据摄取到Google Cloud Storage
import yaml
# 导入所需的Python标准库
import os                  # 用于处理操作系统相关的功能
import logging            # 用于日志记录
import gzip              # 用于处理gzip压缩文件
import shutil            # 用于文件操作

# 导入Airflow相关的库
from airflow import DAG                    # 导入DAG类，用于创建工作流
from airflow.utils.dates import days_ago   # 用于处理日期

# 导入Airflow的操作符
from airflow.operators.bash import BashOperator        # 用于执行bash命令
from airflow.operators.python import PythonOperator    # 用于执行Python函数

# 导入Google Cloud相关的库
from google.cloud import storage    # 用于与Google Cloud Storage交互
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateExternalTableOperator    # 用于创建BigQuery外部表
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyDatasetOperator

# 导入数据处理相关的库
import pyarrow.csv as pv           # 用于读取CSV文件
import pyarrow.parquet as pq      # 用于处理Parquet格式文件


# load setup
def load_config():
    config_path = '/opt/airflow/configs/prod.yml'
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)
config = load_config()

# 设置项目相关的环境变量
PROJECT_ID = config['gcp']['project_id']
BUCKET = config['gcp']['bucket_name']
location = config['gcp']['location']



# 设置本地路径和BigQuery数据集名称
BIGQUERY_DATASET ='raw_dataset'  # BigQuery数据集名称
path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")    # Airflow的本地路径


dataset_file_list = ["fhv_tripdata_2021-01.csv","fhv_tripdata_2021-02.csv","fhv_tripdata_2021-03.csv", "fhv_tripdata_2021-04.csv","fhv_tripdata_2021-05.csv","fhv_tripdata_2021-06.csv"]            # 数据集文件名




def format_to_parquet(src_file):
    """将CSV文件转换为Parquet格式
    
    参数:
        src_file: 源CSV文件路径
    """
    try:
        if not src_file.endswith('.csv'):
            logging.error("目前只接受CSV格式的源文件")
            return
        
        logging.info(f"开始读取CSV文件: {src_file}")
        # 添加CSV读取选项，处理可能的编码和类型问题
        table = pv.read_csv(src_file, parse_options=pv.ParseOptions(
            delimiter=',',
            quote_char='"',
            double_quote=True
        ))
        
        output_file = src_file.replace('.csv', '.parquet')
        logging.info(f"开始写入Parquet文件: {output_file}")
        pq.write_table(table, output_file)
        logging.info(f"成功将CSV转换为Parquet: {output_file}")
        
    except Exception as e:
        logging.error(f"转换过程中发生错误: {str(e)}")
        raise

def upload_to_gcs(bucket, object_name, local_file):
    """上传文件到Google Cloud Storage
    
    参数:
        bucket: GCS存储桶名称
        object_name: 目标路径和文件名
        local_file: 源文件路径和文件名
    """
    # 设置上传大文件的参数
    storage.blob._MAX_MULTIPART_SIZE = 5 * 1024 * 1024  # 设置最大分片大小为5MB
    storage.blob._DEFAULT_CHUNKSIZE = 5 * 1024 * 1024   # 设置默认分片大小为5MB

    client = storage.Client()                # 创建Storage客户端
    bucket = client.bucket(bucket)          # 获取存储桶
    blob = bucket.blob(object_name)         # 创建blob对象
    blob.upload_from_filename(local_file)   # 上传文件

def download_and_extract_gz(src_gz_file, dest_csv_file):
    """将压缩的.gz文件解压缩为CSV文件
    """
    with gzip.open(src_gz_file, 'rb') as f_in:
        with open(dest_csv_file, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

# 设置DAG的默认参数
default_args = {
    "owner": "airflow",                # DAG的所有者
    "start_date": days_ago(1),         # 开始时间为1天前
    "depends_on_past": False,          # 不依赖于过去的执行
    "retries": 1,                      # 失败时重试1次
}

# 使用上下文管理器创建DAG
with DAG(
    dag_id="data_ingestion_gcs_dag_fhv_trip",    
    schedule_interval="@daily",          
    default_args=default_args,           
    catchup=False,                       
    max_active_runs=1,                   
    tags=['dtc-de'],                     
) as dag:
    
    for dataset_file_name in dataset_file_list:
        dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/{dataset_file_name}.gz"

        # 修改task_id，确保每个文件有唯一的task_id
        download_dataset_task = BashOperator(
            task_id=f"download_dataset_task_{dataset_file_name}",    # 添加文件名使task_id唯一
            bash_command=f"curl -sS -L --fail {dataset_url} > {path_to_local_home}/{dataset_file_name}.gz"
        )

        extract_gz_task = PythonOperator(
            task_id=f"extract_gz_task_{dataset_file_name}",          # 添加文件名使task_id唯一
            python_callable=download_and_extract_gz,
            op_kwargs={
                "src_gz_file": f"{path_to_local_home}/{dataset_file_name}.gz",
                "dest_csv_file": f"{path_to_local_home}/{dataset_file_name}",
            },
        )

        parquet_file = dataset_file_name.replace('.csv', '.parquet')

        format_to_parquet_task = PythonOperator(
            task_id=f"format_to_parquet_task_{dataset_file_name}",
            python_callable=format_to_parquet,
            op_kwargs={
                "src_file": f"{path_to_local_home}/{dataset_file_name}",
            },
        )

        local_to_gcs_task = PythonOperator(
            task_id=f"local_to_gcs_task_{dataset_file_name}",         # 添加文件名使task_id唯一
            python_callable=upload_to_gcs,
            op_kwargs={
                "bucket": BUCKET,
                "object_name": f"raw/{parquet_file}",
                "local_file": f"{path_to_local_home}/{parquet_file}",
            },
        )

        table_id = dataset_file_name.replace('.csv', '')
        bigquery_external_table_task = BigQueryCreateExternalTableOperator(
            task_id=f"bigquery_external_table_task_{dataset_file_name}",    # 添加文件名使task_id唯一
            table_resource={
                "tableReference": {
                    "projectId": PROJECT_ID,
                    "datasetId": BIGQUERY_DATASET,
                    "tableId": table_id,
                },
                "externalDataConfiguration": {
                    "sourceFormat": "PARQUET",
                    "sourceUris": [f"gs://{BUCKET}/raw/{parquet_file}"],
                },
            },
        )

        # 创建数据集的任务应该在循环外部，因为只需要创建一次
        if dataset_file_name == dataset_file_list[0]:  # 只在第一次循环时创建数据集
            create_dataset_task = BigQueryCreateEmptyDatasetOperator(
                task_id="create_dataset_task",
                dataset_id=BIGQUERY_DATASET,
                project_id=PROJECT_ID,
                location="asia-east1",
                exists_ok=True
            )
            # 设置任务依赖关系
            download_dataset_task >> extract_gz_task >> format_to_parquet_task >> local_to_gcs_task >> create_dataset_task >> bigquery_external_table_task
        else:
            # 对其他文件，跳过创建数据集的步骤
            download_dataset_task >> extract_gz_task >> format_to_parquet_task >> local_to_gcs_task >> bigquery_external_table_task