{{ config(
    materialized='incremental',
    unique_key='trip_id',
    partition_by={
        "field": "pickup_datetime",
        "data_type": "timestamp",
        "granularity": "month"
    },
    incremental_strategy='insert_overwrite',
    cluster_by=['pickup_location_id', 'dropoff_location_id']
) }}

{% set months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12'] %}
{% set years = ['2019', '2020', '2021', '2022', '2023'] %}

{% set current_date = modules.datetime.datetime.now() %}
{% set current_month = current_date.strftime('%Y-%m') %}

WITH all_yellow_trips AS (
    {% set sql_list = [] %}
    {% for year in years %}
    {% for month in months %}
    {% set table_name = 'yellow_tripdata_' ~ year ~ '-' ~ month %}
    {% if table_exists('raw_dataset', table_name) %}
    {% set current_year_month = year ~ '-' ~ month %}
    {% set sql %}
    SELECT
        GENERATE_UUID() as trip_id,
        VendorID as vendor_id,
        tpep_pickup_datetime as pickup_datetime,
        tpep_dropoff_datetime as dropoff_datetime,
        passenger_count,
        trip_distance,
        RatecodeID as rate_code_id,
        store_and_fwd_flag,
        PULocationID as pickup_location_id,
        DOLocationID as dropoff_location_id,
        payment_type,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        improvement_surcharge,
        total_amount,
        'yellow' as taxi_type,
        CURRENT_TIMESTAMP() as created_at
    FROM {{ source('raw', table_name) }}
    {% if is_incremental() and current_year_month == current_month %}
    WHERE DATE(tpep_pickup_datetime) >= DATE_SUB(CURRENT_DATE(), INTERVAL 1 MONTH)
    {% endif %}
    {% endset %}
    {% do sql_list.append(sql) %}
    {% endif %}
    {% endfor %}
    {% endfor %}

    {{ sql_list | join(' UNION ALL ') }}
)

SELECT * FROM all_yellow_trips