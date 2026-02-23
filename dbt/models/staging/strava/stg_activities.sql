{{ config(
    materialized='incremental',
    unique_key='activity_id',
    on_schema_change='fail'
) }}

WITH ranked AS (
    SELECT
        SAFE_CAST(id AS INT64) AS activity_id,
        SAFE_CAST(athlete.id AS INT64) AS athlete_id,
        SAFE_CAST(map.id AS STRING) AS map_id,
        SAFE_CAST(gear_id AS STRING) AS gear_id,

        SAFE_CAST(name AS STRING) AS activity_name,
        SAFE_CAST(sport_type AS STRING) AS discipline,
        SAFE_CAST(workout_type AS INT64) AS workout_type,
        SAFE_CAST(distance AS FLOAT64) AS distance_m,
        SAFE_CAST(moving_time AS INT64) AS moving_time_s,
        SAFE_CAST(elapsed_time AS INT64) AS elapsed_time_s,
        SAFE_CAST(total_elevation_gain AS FLOAT64) AS elevation_gain_m,

        TIMESTAMP(start_date) AS start_date_utc,
        TIMESTAMP(start_date_local) AS start_date_local,
        SAFE_CAST(timezone AS STRING) AS timezone,
        SAFE_CAST(utc_offset AS INT64) AS utc_offset_s,

        location_city,
        location_state,
        location_country,

        SAFE_CAST(achievement_count AS INT64) AS achievement_count,
        SAFE_CAST(kudos_count AS INT64) AS kudos_count,
        SAFE_CAST(comment_count AS INT64) AS comment_count,
        SAFE_CAST(athlete_count AS INT64) AS athlete_count,
        SAFE_CAST(photo_count AS INT64) AS photo_count,

        SAFE_CAST(trainer AS BOOL) AS is_trainer,
        SAFE_CAST(commute AS BOOL) AS is_commute,
        SAFE_CAST(manual AS BOOL) AS is_manual,
        SAFE_CAST(flagged AS BOOL) AS is_flagged,
        SAFE_CAST(has_heartrate AS BOOL) AS has_heartrate,
        SAFE_CAST(visibility AS STRING) AS visibility,

        SAFE_CAST(average_speed AS FLOAT64) AS avg_speed_mps,
        SAFE_CAST(max_speed AS FLOAT64) AS max_speed_mps,
        SAFE_CAST(average_heartrate AS FLOAT64) AS avg_heartrate,
        SAFE_CAST(max_heartrate AS FLOAT64) AS max_heartrate,
        SAFE_CAST(average_cadence AS FLOAT64) AS avg_cadence,
        SAFE_CAST(average_temp AS FLOAT64) AS avg_temp_c,
        SAFE_CAST(kilojoules AS FLOAT64) AS energy_kj,
        SAFE_CAST(average_watts AS FLOAT64) AS avg_watts,
        SAFE_CAST(max_watts AS FLOAT64) AS max_watts,
        SAFE_CAST(weighted_average_watts AS FLOAT64) AS weighted_watts,
        SAFE_CAST(elev_high AS FLOAT64) AS elev_high_m,
        SAFE_CAST(elev_low AS FLOAT64) AS elev_low_m,

        map.summary_polyline AS map_polyline,
        SAFE_CAST(upload_id AS INT64) AS upload_id,
        SAFE_CAST(upload_id_str AS STRING) AS upload_id_str,
        SAFE_CAST(external_id AS STRING) AS external_id,

        SAFE_CAST(ingested_at AS TIMESTAMP) AS ingested_at,
        CURRENT_TIMESTAMP() AS processed_at,

        ROW_NUMBER() OVER (
            PARTITION BY id
            ORDER BY ingested_at DESC
        ) AS rn
    FROM {{ source('strava_data', 'raw_activities') }}
),

final AS (
    SELECT *
    FROM ranked
    WHERE rn = 1
)

SELECT
    activity_id,
    athlete_id,
    map_id,
    gear_id,
    activity_name,
    discipline,
    workout_type,
    distance_m,
    moving_time_s,
    elapsed_time_s,
    elevation_gain_m,
    start_date_utc,
    start_date_local,
    timezone,
    utc_offset_s,
    location_city,
    location_state,
    location_country,
    achievement_count,
    kudos_count,
    comment_count,
    athlete_count,
    photo_count,
    is_trainer,
    is_commute,
    is_manual,
    is_flagged,
    has_heartrate,
    visibility,
    avg_speed_mps,
    max_speed_mps,
    avg_heartrate,
    max_heartrate,
    avg_cadence,
    avg_temp_c,
    energy_kj,
    avg_watts,
    max_watts,
    weighted_watts,
    elev_high_m,
    elev_low_m,
    map_polyline,
    upload_id,
    upload_id_str,
    external_id,
    ingested_at,
    processed_at,

    EXTRACT(DATE FROM start_date_local) AS activity_date_local,
    EXTRACT(YEAR FROM start_date_local) AS activity_year,
    EXTRACT(MONTH FROM start_date_local) AS activity_month,
    EXTRACT(DAYOFWEEK FROM start_date_local) AS activity_weekday,
    EXTRACT(HOUR FROM start_date_local) AS activity_hour_local,

    SAFE_DIVIDE(moving_time_s / 60.0, distance_m / 1000.0) AS avg_pace_min_per_km,
    SAFE_DIVIDE(moving_time_s, SAFE_DIVIDE(distance_m, 1000.0)) AS pace_sec_per_km,
    avg_speed_mps * 3.6 AS avg_speed_kph,
    max_speed_mps * 3.6 AS max_speed_kph,
    SAFE_DIVIDE(distance_m, elapsed_time_s) * 3.6 AS avg_speed_overall_kph,
    (elapsed_time_s - moving_time_s) AS idle_time_s

FROM final
