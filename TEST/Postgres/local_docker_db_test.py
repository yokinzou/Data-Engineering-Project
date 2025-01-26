import psycopg2
import pandas as pd

def query_postgres():
    # 连接参数
    conn_params = {
        'host': 'localhost',  # docker-compose 中的服务名
        'port': '5432',
        'database': 'airflow',
        'user': 'airflow',
        'password': 'airflow'
    }
    
    # 建立连接
    conn = psycopg2.connect(**conn_params)
    
    # 执行查询
    query = """
        SELECT 
            COUNT(*) as trip_count
         
        FROM yellow_taxi_trips
      
    """
    
    df = pd.read_sql(query, conn)
    print(df.head())
    
    conn.close()

query_postgres()
