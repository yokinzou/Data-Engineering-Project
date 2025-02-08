{% macro get_green_tripdata_tables() %}
  {% set tables = [] %}
  
  {% for node in graph.sources.values() %}
    {% if node.source_name == 'staging' and node.name.startswith('green_tripdata_') %}
      {% do tables.append(node) %}
    {% endif %}
  {% endfor %}
  
  {% set tables = tables | sort(attribute='name') %}
  
  {% for table in tables %}
    select * from {{ source('staging', table.name) }}
    {% if not loop.last %} union all {% endif %}
  {% endfor %}
{% endmacro %}