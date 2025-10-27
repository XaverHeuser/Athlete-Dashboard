{{ config(materialized='view') }}

with base as (
    select
        -- Identifiers (may exist in your raw table; keep if present)
        SAFE_CAST(athlete_id AS INT64) AS athlete_id,
        timestamp(fetched_at) as fetched_at,

        -- Top-level stats (meters)
        SAFE_CAST(biggest_ride_distance AS FLOAT64) AS biggest_ride_distance_m,
        SAFE_CAST(biggest_climb_elevation_gain AS FLOAT64) AS biggest_climb_elevation_gain_m,

        -- ----------------------------
        -- Recent totals (ride / run / swim)
        -- ----------------------------
        SAFE_CAST(recent_ride_totals.count AS INT64) AS recent_ride_count,
        SAFE_CAST(recent_ride_totals.distance AS FLOAT64) AS recent_ride_distance_m,
        SAFE_CAST(recent_ride_totals.moving_time AS INT64) AS recent_ride_moving_time_s,
        SAFE_CAST(recent_ride_totals.elapsed_time AS INT64) AS recent_ride_elapsed_time_s,
        SAFE_CAST(recent_ride_totals.elevation_gain AS FLOAT64) AS recent_ride_elevation_gain_m,
        SAFE_CAST(recent_ride_totals.achievement_count AS INT64) AS recent_ride_achievement_count,

        SAFE_CAST(recent_run_totals.count AS INT64) AS recent_run_count,
        SAFE_CAST(recent_run_totals.distance AS FLOAT64) AS recent_run_distance_m,
        SAFE_CAST(recent_run_totals.moving_time AS INT64) AS recent_run_moving_time_s,
        SAFE_CAST(recent_run_totals.elapsed_time AS INT64) AS recent_run_elapsed_time_s,
        SAFE_CAST(recent_run_totals.elevation_gain AS FLOAT64) AS recent_run_elevation_gain_m,
        SAFE_CAST(recent_run_totals.achievement_count AS INT64) AS recent_run_achievement_count,

        SAFE_CAST(recent_swim_totals.count AS INT64) AS recent_swim_count,
        SAFE_CAST(recent_swim_totals.distance AS FLOAT64) AS recent_swim_distance_m,
        SAFE_CAST(recent_swim_totals.moving_time AS INT64) AS recent_swim_moving_time_s,
        SAFE_CAST(recent_swim_totals.elapsed_time AS INT64) AS recent_swim_elapsed_time_s,
        SAFE_CAST(recent_swim_totals.elevation_gain AS FLOAT64) AS recent_swim_elevation_gain_m,
        SAFE_CAST(recent_swim_totals.achievement_count AS INT64) AS recent_swim_achievement_count,

        -- ----------------------------
        -- All-time totals (ride / run / swim)
        -- ----------------------------
        SAFE_CAST(all_ride_totals.count AS INT64) AS all_ride_count,
        SAFE_CAST(all_ride_totals.distance AS FLOAT64) AS all_ride_distance_m,
        SAFE_CAST(all_ride_totals.moving_time AS INT64) AS all_ride_moving_time_s,
        SAFE_CAST(all_ride_totals.elapsed_time AS INT64) AS all_ride_elapsed_time_s,
        SAFE_CAST(all_ride_totals.elevation_gain AS FLOAT64) AS all_ride_elevation_gain_m,

        SAFE_CAST(all_run_totals.count AS INT64) AS all_run_count,
        SAFE_CAST(all_run_totals.distance AS FLOAT64) AS all_run_distance_m,
        SAFE_CAST(all_run_totals.moving_time AS INT64) AS all_run_moving_time_s,
        SAFE_CAST(all_run_totals.elapsed_time AS INT64) AS all_run_elapsed_time_s,
        SAFE_CAST(all_run_totals.elevation_gain AS FLOAT64) AS all_run_elevation_gain_m,

        SAFE_CAST(all_swim_totals.count AS INT64) AS all_swim_count,
        SAFE_CAST(all_swim_totals.distance AS FLOAT64) AS all_swim_distance_m,
        SAFE_CAST(all_swim_totals.moving_time AS INT64) AS all_swim_moving_time_s,
        SAFE_CAST(all_swim_totals.elapsed_time AS INT64) AS all_swim_elapsed_time_s,
        SAFE_CAST(all_swim_totals.elevation_gain AS FLOAT64) AS all_swim_elevation_gain_m,

        -- ----------------------------
        -- Year-to-date totals (ride / run / swim)
        -- ----------------------------
        SAFE_CAST(ytd_ride_totals.count AS INT64) AS ytd_ride_count,
        SAFE_CAST(ytd_ride_totals.distance AS FLOAT64) AS ytd_ride_distance_m,
        SAFE_CAST(ytd_ride_totals.moving_time AS FLOAT64) AS ytd_ride_moving_time_s,
        SAFE_CAST(ytd_ride_totals.elapsed_time AS FLOAT64) AS ytd_ride_elapsed_time_s,
        SAFE_CAST(ytd_ride_totals.elevation_gain AS FLOAT64) AS ytd_ride_elevation_gain_m,

        SAFE_CAST(ytd_run_totals.count AS INT64) AS ytd_run_count,
        SAFE_CAST(ytd_run_totals.distance AS FLOAT64) AS ytd_run_distance_m,
        SAFE_CAST(ytd_run_totals.moving_time AS FLOAT64) AS ytd_run_moving_time_s,
        SAFE_CAST(ytd_run_totals.elapsed_time AS FLOAT64) AS ytd_run_elapsed_time_s,
        SAFE_CAST(ytd_run_totals.elevation_gain AS FLOAT64) AS ytd_run_elevation_gain_m,

        SAFE_CAST(ytd_swim_totals.count AS INT64) AS ytd_swim_count,
        SAFE_CAST(ytd_swim_totals.distance AS FLOAT64) AS ytd_swim_distance_m,
        SAFE_CAST(ytd_swim_totals.moving_time AS FLOAT64) AS ytd_swim_moving_time_s,
        SAFE_CAST(ytd_swim_totals.elapsed_time AS FLOAT64) AS ytd_swim_elapsed_time_s,
        SAFE_CAST(ytd_swim_totals.elevation_gain AS FLOAT64) AS ytd_swim_elevation_gain_m,

        -- Metadata
        CURRENT_TIMESTAMP() AS _staged_at

    from {{ source('strava_data', 'raw_athlete_stats') }}
)

select * from base
