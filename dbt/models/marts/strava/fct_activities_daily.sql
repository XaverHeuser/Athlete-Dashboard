{{
  config(
    materialized='table',
    cluster_by=['sport_type', 'activity_date']
  )
}}

WITH stg AS (
    SELECT
        activity_id,
        sport_type,
        DATE(start_date_local) AS activity_date,
        distance_m,
        moving_time_s,
        elevation_gain_m
    FROM {{ ref('stg_activities') }}
    WHERE sport_type IS NOT NULL
),

date_bounds AS (
    SELECT
        MIN(activity_date) AS min_activity_date
    FROM stg
),

sport_types AS (
    SELECT DISTINCT sport_type
    FROM stg
)

SELECT
    s.sport_type,
    d.date_day AS activity_date,

    COALESCE(SUM(a.distance_m) / 1000, 0) AS total_distance_km,
    COALESCE(SUM(a.moving_time_s) / 3600.0, 0) AS total_moving_time_h,
    COALESCE(SUM(a.elevation_gain_m), 0) AS total_elevation_gain_m,
    COALESCE(COUNT(a.activity_id), 0) AS total_activities,

    CURRENT_TIMESTAMP() AS mart_loaded_at

FROM {{ ref('dim_date') }} d
CROSS JOIN sport_types s
LEFT JOIN stg a
    ON a.activity_date = d.date_day
   AND a.sport_type = s.sport_type

WHERE d.date_day BETWEEN
    (SELECT min_activity_date FROM date_bounds)
    AND CURRENT_DATE()

GROUP BY
    s.sport_type,
    d.date_day
