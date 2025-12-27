{{
  config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key=['athlete_id', 'snapshot_date'],
    partition_by={'field': 'snapshot_date', 'data_type': 'date'},
    cluster_by=['athlete_id'],
    on_schema_change='fail'
  )
}}

WITH src AS (
  SELECT
    s.athlete_id,
    s.fetched_at AS snapshot_ts,
    DATE(s.fetched_at, 'Europe/Berlin') AS snapshot_date,

    s.biggest_ride_distance_m,
    s.biggest_climb_elevation_gain_m,

    s.recent_ride_count, s.recent_ride_distance_m, s.recent_ride_moving_time_s,
    s.recent_ride_elapsed_time_s, s.recent_ride_elevation_gain_m, s.recent_ride_achievement_count,
    s.recent_run_count,  s.recent_run_distance_m,  s.recent_run_moving_time_s,
    s.recent_run_elapsed_time_s,  s.recent_run_elevation_gain_m,  s.recent_run_achievement_count,
    s.recent_swim_count, s.recent_swim_distance_m, s.recent_swim_moving_time_s,
    s.recent_swim_elapsed_time_s, s.recent_swim_elevation_gain_m, s.recent_swim_achievement_count,

    s.all_ride_count, s.all_ride_distance_m, s.all_ride_moving_time_s, s.all_ride_elapsed_time_s, s.all_ride_elevation_gain_m,
    s.all_run_count,  s.all_run_distance_m,  s.all_run_moving_time_s,  s.all_run_elapsed_time_s,  s.all_run_elevation_gain_m,
    s.all_swim_count, s.all_swim_distance_m, s.all_swim_moving_time_s, s.all_swim_elapsed_time_s, s.all_swim_elevation_gain_m,

    s.ytd_ride_count, s.ytd_ride_distance_m, s.ytd_ride_moving_time_s, s.ytd_ride_elapsed_time_s, s.ytd_ride_elevation_gain_m,
    s.ytd_run_count,  s.ytd_run_distance_m,  s.ytd_run_moving_time_s,  s.ytd_run_elapsed_time_s,  s.ytd_run_elevation_gain_m,
    s.ytd_swim_count, s.ytd_swim_distance_m, s.ytd_swim_moving_time_s, s.ytd_swim_elapsed_time_s, s.ytd_swim_elevation_gain_m,

    CURRENT_TIMESTAMP() AS _mart_loaded_at
  FROM {{ ref('stg_athlete_stats') }} s

  {% if is_incremental() %}
  WHERE DATE(s.fetched_at, 'Europe/Berlin') >= DATE_SUB(
    (SELECT COALESCE(MAX(snapshot_date), DATE '1970-01-01') FROM {{ this }}),
    INTERVAL 3 DAY
  )
  {% endif %}
),

dedup_daily AS (
  SELECT * EXCEPT(rn)
  FROM (
    SELECT
      src.*,
      ROW_NUMBER() OVER (PARTITION BY athlete_id, snapshot_date ORDER BY snapshot_ts DESC) AS rn
    FROM src
  )
  WHERE rn = 1
)

SELECT * FROM dedup_daily
