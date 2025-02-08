-- sgt_green_tripdata.sql

{{ config(
    materialized='incremental',
    unique_key='trip_id',
    incremental_strategy='delete+insert',
    on_schema_change='fail'
) }}

with green_tripdata as (
    select 
       *
    from {{ source('staging', 'green_tripdata_external') }}  -- 假设这是一个外部表或视图，包含所有月份数据
    where 1=1
    {% if is_incremental() %}
        -- 这个条件只在增量运行时生效
        and pickup_datetime > (select max(pickup_datetime) from {{ this }})
    {% endif %}
)

select * from green_tripdata