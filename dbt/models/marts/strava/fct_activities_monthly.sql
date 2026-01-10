{{
  config(
    materialized='table',
    cluster_by=['discipline', 'activity_month']
  )
}}

SELECT
    discipline,
    DATE_TRUNC(activity_date, MONTH) AS activity_month,
    
    SUM(total_activities) AS total_activities,
    SUM(total_distance_km) AS total_distance_km,
    SUM(total_moving_time_h) AS total_moving_time_h,
    SUM(total_elevation_gain_m) AS total_elevation_gain_m,

    CURRENT_TIMESTAMP() AS mart_loaded_at
    
FROM {{ ref('fct_activities_daily') }}
GROUP BY 1, 2
