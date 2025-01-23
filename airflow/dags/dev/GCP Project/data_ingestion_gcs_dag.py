# 这是主要的DAG文件，用于数据摄取到Google Cloud Storage

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

# 设置项目相关的环境变量
PROJECT_ID = os.environ.get("PROJECT_ID")              # 获取Google Cloud项目ID
BUCKET = os.environ.get("BUCKET")                 # 获取Google Cloud Storage存储桶名称

# 定义数据集相关的变量
dataset_file = "yellow_tripdata_2021-01.csv"              # 数据集文件名
dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"    # 数据集下载地址

# 设置本地路径和BigQuery数据集名称
path_to_local_home = os.environ.get("AIRFLOW_HOME", "/opt/airflow/")    # Airflow的本地路径
BIGQUERY_DATASET = os.environ.get("BIGQUERY_DATASET", 'trips_data_all')  # BigQuery数据集名称

# 定义Parquet文件名
parquet_file = dataset_file.replace('.csv', '.parquet')    # 将CSV文件名转换为Parquet文件名

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
    
    Args:
        src_gz_file (str): 源.gz文件的路径
        dest_csv_file (str): 目标CSV文件的路径
        
    Returns:
        None
        
    示例:
        download_and_extract_gz(
            "/path/to/data.csv.gz",
            "/path/to/output.csv"
        )
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
    dag_id="data_ingestion_gcs_dag",    # DAG的唯一标识符
    schedule_interval="@daily",          # 设置为每天执行一次
    default_args=default_args,           # 使用上面定义的默认参数
    catchup=False,                       # 不执行历史任务
    max_active_runs=1,                   # 最大同时运行的DAG数量
    tags=['dtc-de'],                     # DAG的标签
) as dag:

    # 定义下载数据集的任务
    download_dataset_task = BashOperator(
        task_id="download_dataset_task",    # 任务的唯一标识符
        bash_command=f"curl -sS -L --fail {dataset_url} > {path_to_local_home}/{dataset_file}.gz"    # 使用curl下载数据集
    )

    # 定义解压gz文件的任务
    extract_gz_task = PythonOperator(
        task_id="extract_gz_task",          # 任务的唯一标识符
        python_callable=download_and_extract_gz,    # 调用的Python函数
        op_kwargs={                         # 传递给函数的参数
            "src_gz_file": f"{path_to_local_home}/{dataset_file}.gz",
            "dest_csv_file": f"{path_to_local_home}/{dataset_file}",
        },
    )

    # 定义转换为Parquet格式的任务
    format_to_parquet_task = PythonOperator(
        task_id="format_to_parquet_task",    # 任务的唯一标识符
        python_callable=format_to_parquet,    # 调用的Python函数
        op_kwargs={
            "src_file": f"{path_to_local_home}/{dataset_file}",
        },
    )

    # 定义上传到GCS的任务
    local_to_gcs_task = PythonOperator(
        task_id="local_to_gcs_task",         # 任务的唯一标识符
        python_callable=upload_to_gcs,        # 调用的Python函数
        op_kwargs={
            "bucket": BUCKET,
            "object_name": f"raw/{parquet_file}",
            "local_file": f"{path_to_local_home}/{parquet_file}",
        },
    )

    # 添加创建数据集的任务
    create_dataset_task = BigQueryCreateEmptyDatasetOperator(
        task_id="create_dataset_task",
        dataset_id=BIGQUERY_DATASET,
        project_id=PROJECT_ID,
        location="asia-east1",  # 指定数据集位置
        exists_ok=True  # 如果数据集已存在则不会报错
    )

    # 定义创建BigQuery外部表的任务
    bigquery_external_table_task = BigQueryCreateExternalTableOperator(
        task_id="bigquery_external_table_task",    # 任务的唯一标识符
        table_resource={                           # 表资源配置
            "tableReference": {
                "projectId": PROJECT_ID,           # Google Cloud项目ID
                "datasetId": BIGQUERY_DATASET,     # BigQuery数据集ID
                "tableId": "yellow_tripdata_2021-01",       # 表ID
            },
            "externalDataConfiguration": {
                "sourceFormat": "PARQUET",         # 源数据格式为Parquet
                "sourceUris": [f"gs://{BUCKET}/raw/{parquet_file}"],    # 数据源URI
            },
        },
    )

    # 设置任务的执行顺序（使用>>操作符表示依赖关系）
    download_dataset_task >> extract_gz_task >> format_to_parquet_task >> local_to_gcs_task >> create_dataset_task >> bigquery_external_table_task