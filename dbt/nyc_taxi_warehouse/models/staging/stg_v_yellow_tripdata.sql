{% set relations = dbt_utils.get_relations_by_pattern('raw_dataset', 'yellow_tripdata_2021-%') %}

{% for relation in relations %}
    select * 
    from {{ source('raw', relation.identifier) }}
    {% if not loop.last %} union all {% endif %}
{% endfor %}