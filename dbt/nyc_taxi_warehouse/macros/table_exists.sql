{% macro table_exists(source_schema, table_name) %}
  {% set query %}
    SELECT COUNT(1) as exists_flag
    FROM `{{ target.project }}.{{ source_schema }}.__TABLES_SUMMARY__`
    WHERE table_id = '{{ table_name }}'
  {% endset %}
  
  {% set results = run_query(query) %}
  
  {% if execute %}
    {% set exists = results.columns[0].values()[0] > 0 %}
    {{ return(exists) }}
  {% else %}
    {{ return(false) }}
  {% endif %}
{% endmacro %}