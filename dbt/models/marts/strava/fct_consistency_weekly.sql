{{
  config(
    materialized='table',
    cluster_by=['discipline', 'activity_week']
  )
}}

WITH w AS (
  SELECT
    discipline,
    SAFE_CAST(activity_week AS DATETIME) AS activity_week,
    total_activities,
    total_distance_km,
    total_moving_time_h,
    total_elevation_gain_m
  FROM {{ ref('fct_activities_weekly') }}
),

final AS (
  SELECT
    discipline,
    activity_week,

    total_activities,
    total_distance_km,
    total_moving_time_h,
    total_elevation_gain_m,

    IF(total_activities > 0 OR total_moving_time_h > 0, 1, 0) AS is_active_week,

    CURRENT_TIMESTAMP() AS mart_loaded_at
  FROM w
)

SELECT * FROM final
