{{ config(materialized='table') }}

WITH stg AS (
    SELECT * FROM {{ ref('stg_activities') }}   -- your staging model
)

SELECT
    activity_id,
    athlete_id,
    gear_id,
    activity_name,
    sport_type,
    start_date_local,
    activity_date_local,
    activity_year,
    activity_month,
    activity_weekday,
    activity_hour_local,

    distance_m,
    distance_m/1000 AS distance_km,
    moving_time_s,
    elapsed_time_s,
    avg_pace_min_per_km,
    avg_speed_kph,
    max_speed_kph,
    avg_speed_overall_kph,

    elevation_gain_m,
    avg_heartrate,
    max_heartrate,
    avg_cadence,
    energy_kj,
    avg_watts,
    max_watts,
    weighted_watts,

    kudos_count,
    comment_count,
    achievement_count,

    is_commute,
    is_trainer,
    has_heartrate,

    map_id,
    map_polyline,

    CURRENT_TIMESTAMP() AS _loaded_at

FROM stg
