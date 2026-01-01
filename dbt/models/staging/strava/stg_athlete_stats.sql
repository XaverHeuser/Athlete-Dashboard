{{ config(materialized='view') }}

with deduplicated as (

    select
        SAFE_CAST(athlete_id AS INT64) AS athlete_id,
        TIMESTAMP(fetched_at) AS fetched_at,
        DATE(fetched_at) AS snapshot_date,

        SAFE_CAST(biggest_ride_distance AS FLOAT64) AS biggest_ride_distance_m,
        SAFE_CAST(biggest_climb_elevation_gain AS FLOAT64) AS biggest_climb_elevation_gain_m,

        -- Ride (recent)
        SAFE_CAST(recent_ride_totals.count AS INT64) AS recent_ride_count,
        SAFE_CAST(recent_ride_totals.distance AS FLOAT64) AS recent_ride_distance_m,
        SAFE_CAST(recent_ride_totals.moving_time AS INT64) AS recent_ride_moving_time_s,
        SAFE_CAST(recent_ride_totals.elapsed_time AS INT64) AS recent_ride_elapsed_time_s,
        SAFE_CAST(recent_ride_totals.elevation_gain AS FLOAT64) AS recent_ride_elevation_gain_m,
        SAFE_CAST(recent_ride_totals.achievement_count AS INT64) AS recent_ride_achievement_count,

        -- Ride (ytd)
        SAFE_CAST(ytd_ride_totals.count AS INT64) AS ytd_ride_count,
        SAFE_CAST(ytd_ride_totals.distance AS FLOAT64) AS ytd_ride_distance_m,
        SAFE_CAST(ytd_ride_totals.moving_time AS INT64) AS ytd_ride_moving_time_s,
        SAFE_CAST(ytd_ride_totals.elapsed_time AS INT64) AS ytd_ride_elapsed_time_s,
        SAFE_CAST(ytd_ride_totals.elevation_gain AS FLOAT64) AS ytd_ride_elevation_gain_m,

        -- Ride (all)
        SAFE_CAST(all_ride_totals.count AS INT64) AS all_ride_count,
        SAFE_CAST(all_ride_totals.distance AS FLOAT64) AS all_ride_distance_m,
        SAFE_CAST(all_ride_totals.moving_time AS INT64) AS all_ride_moving_time_s,
        SAFE_CAST(all_ride_totals.elapsed_time AS INT64) AS all_ride_elapsed_time_s,
        SAFE_CAST(all_ride_totals.elevation_gain AS FLOAT64) AS all_ride_elevation_gain_m,


        -- Run (recent)
        SAFE_CAST(recent_run_totals.count AS INT64) AS recent_run_count,
        SAFE_CAST(recent_run_totals.distance AS FLOAT64) AS recent_run_distance_m,
        SAFE_CAST(recent_run_totals.moving_time AS INT64) AS recent_run_moving_time_s,
        SAFE_CAST(recent_run_totals.elapsed_time AS INT64) AS recent_run_elapsed_time_s,
        SAFE_CAST(recent_run_totals.elevation_gain AS FLOAT64) AS recent_run_elevation_gain_m,
        SAFE_CAST(recent_run_totals.achievement_count AS INT64) AS recent_run_achievement_count,

        -- Run (ytd)
        SAFE_CAST(ytd_run_totals.count AS INT64) AS ytd_run_count,
        SAFE_CAST(ytd_run_totals.distance AS FLOAT64) AS ytd_run_distance_m,
        SAFE_CAST(ytd_run_totals.moving_time AS INT64) AS ytd_run_moving_time_s,
        SAFE_CAST(ytd_run_totals.elapsed_time AS INT64) AS ytd_run_elapsed_time_s,
        SAFE_CAST(ytd_run_totals.elevation_gain AS FLOAT64) AS ytd_run_elevation_gain_m,

        -- Run (all)
        SAFE_CAST(all_run_totals.count AS INT64) AS all_run_count,
        SAFE_CAST(all_run_totals.distance AS FLOAT64) AS all_run_distance_m,
        SAFE_CAST(all_run_totals.moving_time AS INT64) AS all_run_moving_time_s,
        SAFE_CAST(all_run_totals.elapsed_time AS INT64) AS all_run_elapsed_time_s,
        SAFE_CAST(all_run_totals.elevation_gain AS FLOAT64) AS all_run_elevation_gain_m,


        -- Swim (recent)
        SAFE_CAST(recent_swim_totals.count AS INT64) AS recent_swim_count,
        SAFE_CAST(recent_swim_totals.distance AS FLOAT64) AS recent_swim_distance_m,
        SAFE_CAST(recent_swim_totals.moving_time AS INT64) AS recent_swim_moving_time_s,
        SAFE_CAST(recent_swim_totals.elapsed_time AS INT64) AS recent_swim_elapsed_time_s,
        SAFE_CAST(recent_swim_totals.elevation_gain AS FLOAT64) AS recent_swim_elevation_gain_m,
        SAFE_CAST(recent_swim_totals.achievement_count AS INT64) AS recent_swim_achievement_count,

        -- Swim (ytd)
        SAFE_CAST(ytd_swim_totals.count AS INT64) AS ytd_swim_count,
        SAFE_CAST(ytd_swim_totals.distance AS FLOAT64) AS ytd_swim_distance_m,
        SAFE_CAST(ytd_swim_totals.moving_time AS INT64) AS ytd_swim_moving_time_s,
        SAFE_CAST(ytd_swim_totals.elapsed_time AS INT64) AS ytd_swim_elapsed_time_s,
        SAFE_CAST(ytd_swim_totals.elevation_gain AS FLOAT64) AS ytd_swim_elevation_gain_m,

        -- Swim (all)
        SAFE_CAST(all_swim_totals.count AS INT64) AS all_swim_count,
        SAFE_CAST(all_swim_totals.distance AS FLOAT64) AS all_swim_distance_m,
        SAFE_CAST(all_swim_totals.moving_time AS INT64) AS all_swim_moving_time_s,
        SAFE_CAST(all_swim_totals.elapsed_time AS INT64) AS all_swim_elapsed_time_s,
        SAFE_CAST(all_swim_totals.elevation_gain AS FLOAT64) AS all_swim_elevation_gain_m,

        ROW_NUMBER() OVER (
            PARTITION BY athlete_id, DATE(fetched_at)
            ORDER BY fetched_at DESC
        ) AS rn

    from {{ source('strava_data', 'raw_athlete_stats') }}
)

select
    athlete_id,
    fetched_at,
    snapshot_date,

    biggest_ride_distance_m,
    biggest_climb_elevation_gain_m,

    -- Ride / Recent
    recent_ride_count,
    recent_ride_distance_m,
    recent_ride_moving_time_s,
    recent_ride_elapsed_time_s,
    recent_ride_elevation_gain_m,
    recent_ride_achievement_count,

    -- Ride / YTD
    ytd_ride_count,
    ytd_ride_distance_m,
    ytd_ride_moving_time_s,
    ytd_ride_elapsed_time_s,
    ytd_ride_elevation_gain_m,
    
    -- Ride / All
    all_ride_count,
    all_ride_distance_m,
    all_ride_moving_time_s,
    all_ride_elapsed_time_s,
    all_ride_elevation_gain_m,


    -- Run / Recent
    recent_run_count,
    recent_run_distance_m,
    recent_run_moving_time_s,
    recent_run_elapsed_time_s,
    recent_run_elevation_gain_m,
    recent_run_achievement_count,

    -- Run / YTD
    ytd_run_count,
    ytd_run_distance_m,
    ytd_run_moving_time_s,
    ytd_run_elapsed_time_s,
    ytd_run_elevation_gain_m,

    -- Run / All
    all_run_count,
    all_run_distance_m,
    all_run_moving_time_s,
    all_run_elapsed_time_s,
    all_run_elevation_gain_m,


    -- Swim / Recent
    recent_swim_count,
    recent_swim_distance_m,
    recent_swim_moving_time_s,
    recent_swim_elapsed_time_s,
    recent_swim_elevation_gain_m,
    recent_swim_achievement_count,

    -- Swim / YTD
    ytd_swim_count,
    ytd_swim_distance_m,
    ytd_swim_moving_time_s,
    ytd_swim_elapsed_time_s,
    ytd_swim_elevation_gain_m,

    -- Swim / All
    all_swim_count,
    all_swim_distance_m,
    all_swim_moving_time_s,
    all_swim_elapsed_time_s,
    all_swim_elevation_gain_m

from deduplicated
where rn = 1
