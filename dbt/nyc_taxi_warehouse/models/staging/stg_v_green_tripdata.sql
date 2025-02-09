

select * from {{ source('raw', 'green_tripdata_2021-01') }}