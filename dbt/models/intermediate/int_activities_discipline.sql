{{ config(materialized='view') }}

WITH mapped AS (
  SELECT
    activity_id,
    {{ map_discipline('discipline') }} AS discipline,
    DATE(start_date_local) AS activity_date,
    distance_m,
    moving_time_s,
    elevation_gain_m
  FROM {{ ref('stg_activities') }}
  WHERE discipline IS NOT NULL
)
SELECT *
FROM mapped
WHERE discipline IS NOT NULL
