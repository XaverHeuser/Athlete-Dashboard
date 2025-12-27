-- models/marts/strava/fct_athlete_stats_latest.sql
{{ config(materialized='view') }}

WITH ranked AS (
  SELECT
    f.*,
    ROW_NUMBER() OVER (
      PARTITION BY athlete_id
      ORDER BY snapshot_ts DESC, snapshot_date DESC, _mart_loaded_at DESC
    ) AS rn
  FROM {{ ref('fct_athlete_stats_snapshot_daily') }} f
)

SELECT * EXCEPT(rn)
FROM ranked
WHERE rn = 1
