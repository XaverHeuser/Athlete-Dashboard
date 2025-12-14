{{ config(materialized='table') }}

SELECT
    sport_type,
    DATE_TRUNC(activity_date, YEAR) AS activity_year,
    SUM(total_activities) AS total_activities,
    SUM(total_distance_m) AS total_distance_m,
    SUM(total_moving_time_s) AS total_moving_time_s,
    SUM(total_elevation_gain_m) AS total_elevation_gain_m
FROM {{ ref('fct_activities_daily') }}
GROUP BY
    sport_type,
    activity_year
