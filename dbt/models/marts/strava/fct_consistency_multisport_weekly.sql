{{
  config(
    materialized='view'
  )
}}

WITH w AS (
  SELECT
    activity_week,

    MAX(IF(discipline='Run', is_active_week, 0)) AS run_active,
    MAX(IF(discipline='Ride', is_active_week, 0)) AS ride_active,
    MAX(IF(discipline='Swim', is_active_week, 0)) AS swim_active,
    MAX(IF(discipline='Strength', is_active_week, 0)) AS strength_active,

    SUM(total_activities) AS total_activities

  FROM {{ ref('fct_consistency_weekly') }}
  GROUP BY 1
)

SELECT
  *,
  IF(run_active=1 AND ride_active=1 AND swim_active=1, 1, 0) AS triathlon_covered,
  IF(run_active=1 AND ride_active=1 AND swim_active=1 AND strength_active=1, 1, 0) AS all4_covered,

  CURRENT_TIMESTAMP() AS mart_loaded_at
FROM w
