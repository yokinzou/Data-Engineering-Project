{{ config(
    materialized='table'
) }}

SELECT 
    CAST(NULL AS STRING) as trip_id,
    CAST(NULL AS INT64) as vendor_key,
    CAST(NULL AS INT64) as pickup_datetime_key,
    CAST(NULL AS INT64) as dropoff_datetime_key,
    CAST(NULL AS INT64) as pickup_location_key,
    CAST(NULL AS INT64) as dropoff_location_key,
    CAST(NULL AS INT64) as payment_type_key,
    CAST(NULL AS INT64) as taxi_type_key,
    
    -- 度量
    CAST(NULL AS INT64) as passenger_count,
    CAST(NULL AS FLOAT64) as trip_distance,
    CAST(NULL AS FLOAT64) as fare_amount,
    CAST(NULL AS FLOAT64) as extra,
    CAST(NULL AS FLOAT64) as mta_tax,
    CAST(NULL AS FLOAT64) as tip_amount,
    CAST(NULL AS FLOAT64) as tolls_amount,
    CAST(NULL AS FLOAT64) as improvement_surcharge,
    CAST(NULL AS FLOAT64) as total_amount,
    CAST(NULL AS FLOAT64) as congestion_surcharge,
    
    -- 其他属性
    CAST(NULL AS STRING) as store_and_fwd_flag,
    CAST(NULL AS INT64) as rate_code_id,
    CAST(NULL AS INT64) as trip_type,
    CAST(NULL AS INT64) as ehail_fee,
    
    -- 元数据
    CAST(NULL AS STRING) as data_source,
    CAST(NULL AS TIMESTAMP) as created_at
