{{ config(materialized='view') }}

WITH base_raw AS (
    SELECT
        -- Core identifiers
        SAFE_CAST(id AS INT64) AS activity_id,
        SAFE_CAST(athlete.id AS INT64) AS athlete_id,
        SAFE_CAST(map.id AS STRING) AS map_id,
        SAFE_CAST(gear_id AS STRING) AS gear_id,

        -- Basic info
        SAFE_CAST(name AS STRING) AS activity_name,
        SAFE_CAST(sport_type AS STRING) AS sport_type,
        SAFE_CAST(workout_type AS INT64) AS workout_type,
        SAFE_CAST(distance AS FLOAT64) AS distance_m,
        SAFE_CAST(moving_time AS INT64) AS moving_time_s,
        SAFE_CAST(elapsed_time AS INT64) AS elapsed_time_s,
        SAFE_CAST(total_elevation_gain AS FLOAT64) AS elevation_gain_m,

        -- Timestamps (raw)
        TIMESTAMP(start_date) AS start_date_utc,
        TIMESTAMP(start_date_local) AS start_date_local,
        SAFE_CAST(timezone AS STRING) AS timezone,
        SAFE_CAST(utc_offset AS INT64) AS utc_offset_s,

        -- Location
        location_city,
        location_state,
        location_country,

        -- Engagement
        SAFE_CAST(achievement_count AS INT64) AS achievement_count,
        SAFE_CAST(kudos_count AS INT64) AS kudos_count,
        SAFE_CAST(comment_count AS INT64) AS comment_count,
        SAFE_CAST(athlete_count AS INT64) AS athlete_count,
        SAFE_CAST(photo_count AS INT64) AS photo_count,

        -- Boolean flags
        SAFE_CAST(trainer AS BOOL) AS is_trainer,
        SAFE_CAST(commute AS BOOL) AS is_commute,
        SAFE_CAST(manual AS BOOL) AS is_manual,
        SAFE_CAST(flagged AS BOOL) AS is_flagged,
        SAFE_CAST(has_heartrate AS BOOL) AS has_heartrate,
        SAFE_CAST(visibility AS STRING) AS visibility,

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
        SAFE_CAST(elev_high AS FLOAT64) AS elev_high_m,
        SAFE_CAST(elev_low AS FLOAT64) AS elev_low_m,

        -- Map info
        map.summary_polyline AS map_polyline,

        -- External identifiers / lineage
        SAFE_CAST(upload_id AS INT64) AS upload_id,
        SAFE_CAST(upload_id_str AS STRING) AS upload_id_str,
        SAFE_CAST(external_id AS STRING) AS external_id,

        -- Metadata
        CURRENT_TIMESTAMP() AS _staged_at

    FROM {{ source('strava_data', 'raw_activities') }}
),

base_enriched AS (
    SELECT
        br.*,

        -- Time breakdowns (now we can reference start_date_local alias)
        EXTRACT(DATE FROM br.start_date_local) AS activity_date_local,
        EXTRACT(YEAR FROM br.start_date_local) AS activity_year,
        EXTRACT(MONTH FROM br.start_date_local) AS activity_month,
        EXTRACT(DAYOFWEEK FROM br.start_date_local) AS activity_weekday,
        EXTRACT(HOUR FROM br.start_date_local) AS activity_hour_local,

        -- Derived performance metrics using the cleaned columns
        SAFE_DIVIDE(br.moving_time_s / 60.0, br.distance_m / 1000.0) AS avg_pace_min_per_km,
        br.avg_speed_mps * 3.6 AS avg_speed_kph,
        br.max_speed_mps * 3.6 AS max_speed_kph,

        -- Optional but highly useful extras you will probably want:
        SAFE_DIVIDE(br.distance_m, br.elapsed_time_s) * 3.6 AS avg_speed_overall_kph,
        (br.elapsed_time_s - br.moving_time_s) AS idle_time_s

    FROM base_raw br
)

SELECT * FROM base_enriched;
