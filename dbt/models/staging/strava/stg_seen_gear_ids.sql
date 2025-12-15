{{ 
  config(
    materialized = 'incremental',
    unique_key = 'gear_id'
  ) 
}}

WITH src AS (
  SELECT
    gear_id,
    MAX(start_date_local) AS last_seen_at
  FROM {{ ref('stg_activities') }}
  WHERE gear_id IS NOT NULL
  GROUP BY gear_id
)

SELECT
  gear_id,
  last_seen_at
FROM src
