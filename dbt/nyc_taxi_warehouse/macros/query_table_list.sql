{% macro generate_table_list(schema_name, table_name_pattern) %}
  {% set table_list_query %}
      SELECT table_name
      FROM {{ source('your_source_name', '__dbt_source_relation__').database }}.INFORMATION_SCHEMA.TABLES
      WHERE table_schema = '{{ schema_name }}'
        AND table_name LIKE '{{ table_name_pattern }}%'
  {% endset %}

  {% set results = run_query(table_list_query) %}

  {% if execute %}
    {% set table_list = results.columns[0].values() %}
    {{ return(table_list) }}
  {% else %}
    {{ return([]) }}
  {% endif %}

{% endmacro %}