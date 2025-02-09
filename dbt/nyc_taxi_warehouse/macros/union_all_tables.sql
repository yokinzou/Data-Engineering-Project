{% macro union_all_tables(source_name, table_name_pattern) %}
    {% set get_tables_query %}
        SELECT table_name 
        FROM `{{ target.project }}.{{ source_name }}.INFORMATION_SCHEMA.TABLES`
        WHERE table_name LIKE '{{ table_name_pattern }}%'
        ORDER BY table_name
    {% endset %}
    
    {% set results = run_query(get_tables_query) %}
    
    {% if execute %}
        {% set tables = results.columns[0].values() %}
    {% else %}
        {% set tables = [] %}
    {% endif %}
    
    {% if tables|length == 0 %}
        {{ exceptions.raise_compiler_error("没有找到匹配的表: " ~ source_name ~ "." ~ table_name_pattern) }}
    {% endif %}
    
    {% for table in tables %}
        SELECT * FROM `{{ target.project }}.{{ source_name }}.{{ table }}`
        {% if not loop.last %} UNION ALL {% endif %}
    {% endfor %}
{% endmacro %}