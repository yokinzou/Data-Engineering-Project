{% macro generate_table_names(prefix, start_month, end_month) %}
  {% set table_names = [] %}
  {% for month in range(start_month, end_month + 1) %}
    {% set table_name = prefix ~ '_2021-' ~ '%02d' | format(month) %}
    {% do table_names.append(table_name) %}
  {% endfor %}
  {{ return(table_names) }}
{% endmacro %}