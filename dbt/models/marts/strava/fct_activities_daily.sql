{{
    config(
        materialized='table',
        cluster_by=['discipline', 'activity_date']
    )
}}

WITH stg AS (
    SELECT
        activity_id,
        discipline,
        activity_date,
        distance_m,
        moving_time_s,
        elevation_gain_m
    FROM {{ ref('int_activities_discipline') }}
    WHERE discipline IS NOT NULL
),

date_bounds AS (
    SELECT MIN(activity_date) AS min_activity_date
    FROM stg
)

SELECT
    d.discipline,
    dd.date_day AS activity_date,

    COALESCE(SUM(s.distance_m) / 1000, 0) AS total_distance_km,
    COALESCE(SUM(s.moving_time_s) / 3600.0, 0) AS total_moving_time_h,
    COALESCE(SUM(s.elevation_gain_m), 0) AS total_elevation_gain_m,
    COALESCE(COUNT(s.activity_id), 0) AS total_activities,

    CURRENT_TIMESTAMP() AS mart_loaded_at

FROM {{ ref('dim_date') }} dd
CROSS JOIN {{ ref('dim_discipline') }} d
LEFT JOIN stg s
    ON s.activity_date = dd.date_day
    AND s.discipline = d.discipline

WHERE dd.date_day BETWEEN
    (SELECT min_activity_date FROM date_bounds)
    AND CURRENT_DATE()

GROUP BY
    d.discipline,
    dd.date_day
