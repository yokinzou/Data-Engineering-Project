-- sgt_yellow_tripdata.sql

{{ config(materialized='view') }}

with yellow_tripdata as (
    select * from {{ source('staging', 'yellow_tripdata_2021-01') }}
    union all
    select * from {{ source('staging', 'yellow_tripdata_2021-02') }}
    union all
    select * from {{ source('staging', 'yellow_tripdata_2021-03') }}
    union all
    select * from {{ source('staging', 'yellow_tripdata_2021-04') }}
    union all
    select * from {{ source('staging', 'yellow_tripdata_2021-05') }}
    union all
    select * from {{ source('staging', 'yellow_tripdata_2021-06') }}
)

select * from yellow_tripdata
limit 1000


