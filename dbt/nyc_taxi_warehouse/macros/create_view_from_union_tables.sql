{% macro create_view_from_union_tables(view_name, table_name_pattern) %}
    create or replace view {{ target.schema }}.{{ view_name }} as
    {{ union_all_tables('raw', table_name_pattern) }} 
{% endmacro %}          