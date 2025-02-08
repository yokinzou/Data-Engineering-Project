{% macro create_external_table() %}
    create or replace view {{ source('staging', 'green_tripdata_external') }} as
    {{ get_green_tripdata_tables() }}
{% endmacro %}