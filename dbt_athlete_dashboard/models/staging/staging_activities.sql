{{ config(materialized='view') }}

WITH base AS (
    SELECT
        -- Core identifiers
        SAFE_CAST(id AS INT64) AS activity_id,
        SAFE_CAST(athlete.id AS INT64) AS athlete_id,
        SAFE_CAST(map.id AS STRING) AS map_id,

        -- Basic info
        name,
        type,
        sport_type,
        SAFE_CAST(distance AS FLOAT64) AS distance_m,
        SAFE_CAST(moving_time AS INT64) AS moving_time_s,
        SAFE_CAST(elapsed_time AS INT64) AS elapsed_time_s,
        SAFE_CAST(total_elevation_gain AS FLOAT64) AS elevation_gain_m,

        -- Timestamps
        TIMESTAMP(start_date) AS start_date_utc,
        TIMESTAMP(start_date_local) AS start_date_local,
        timezone,
        SAFE_CAST(utc_offset AS FLOAT64) AS utc_offset_s,

        -- Location
        location_city,
        location_state,
        location_country,

        -- Performance
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

        -- Meta flags
        SAFE_CAST(trainer AS BOOL) AS is_trainer,
        SAFE_CAST(commute AS BOOL) AS is_commute,
        SAFE_CAST(manual AS BOOL) AS is_manual,
        SAFE_CAST(private AS BOOL) AS is_private,
        visibility,
        SAFE_CAST(flagged AS BOOL) AS is_flagged,
        SAFE_CAST(has_heartrate AS BOOL) AS has_heartrate,

        -- Engagement
        SAFE_CAST(achievement_count AS INT64) AS achievement_count,
        SAFE_CAST(kudos_count AS INT64) AS kudos_count,
        SAFE_CAST(comment_count AS INT64) AS comment_count,
        SAFE_CAST(photo_count AS INT64) AS photo_count,

        -- Map info
        map.summary_polyline AS map_polyline,
        SAFE_CAST(map.resource_state AS INT64) AS map_resource_state,

        -- Upload
        SAFE_CAST(upload_id AS INT64) AS upload_id,
        SAFE_CAST(upload_id_str AS STRING) AS upload_id_str,
        external_id,

        -- Metadata
        SAFE_CAST(resource_state AS INT64) AS resource_state,
        CURRENT_TIMESTAMP() AS _staged_at


    FROM {{ source('strava_data', 'raw_activities') }}
)

SELECT * FROM base
