{{
  config(
    materialized='table',
    cluster_by=['sport_type', 'activity_month']
  )
}}

SELECT
    sport_type,
    DATE_TRUNC(activity_date, MONTH) AS activity_month,
    
    SUM(total_activities) AS total_activities,
    SUM(total_distance_km) AS total_distance_km,
    SUM(total_moving_time_h) AS total_moving_time_h,
    SUM(total_elevation_gain_m) AS total_elevation_gain_m,

    CURRENT_TIMESTAMP() AS _mart_loaded_at
    
FROM {{ ref('fct_activities_daily') }}
GROUP BY
    sport_type,
    activity_month
