{% macro map_discipline(discipline_col) -%}
CASE
  WHEN LOWER({{ discipline_col }}) IN ('run','trailrun','virtualrun') THEN 'Run'
  WHEN LOWER({{ discipline_col }}) IN ('ride','virtualride','mountainbikeride','gravelride','ebikeride') THEN 'Ride'
  WHEN LOWER({{ discipline_col }}) IN ('swim') THEN 'Swim'
  WHEN LOWER({{ discipline_col }}) IN ('weighttraining','strengthtraining','workout') THEN 'Strength'
  ELSE NULL
END
{%- endmacro %}
