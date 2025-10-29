{{ config(
  materialized='incremental',
  incremental_strategy='merge',
  unique_key='athlete_id_snapshot_date',
  partition_by={'field': 'snapshot_date', 'data_type': 'date'},
  cluster_by=['athlete_id']
) }}

with src as (
  select
    s.athlete_id,
    -- Use the persisted fetch time from staging
    s.fetched_at as snapshot_ts,
    -- Choose your reporting day; here we align to your local tz (Europe/Berlin)
    date(s.fetched_at, 'Europe/Berlin') as snapshot_date,

    -- Top-level
    s.biggest_ride_distance_m,
    s.biggest_climb_elevation_gain_m,

    -- recent_*
    s.recent_ride_count, s.recent_ride_distance_m, s.recent_ride_moving_time_s,
    s.recent_ride_elapsed_time_s, s.recent_ride_elevation_gain_m, s.recent_ride_achievement_count,
    s.recent_run_count,  s.recent_run_distance_m,  s.recent_run_moving_time_s,
    s.recent_run_elapsed_time_s,  s.recent_run_elevation_gain_m,  s.recent_run_achievement_count,
    s.recent_swim_count, s.recent_swim_distance_m, s.recent_swim_moving_time_s,
    s.recent_swim_elapsed_time_s, s.recent_swim_elevation_gain_m, s.recent_swim_achievement_count,

    -- all_*
    s.all_ride_count, s.all_ride_distance_m, s.all_ride_moving_time_s, s.all_ride_elapsed_time_s, s.all_ride_elevation_gain_m,
    s.all_run_count,  s.all_run_distance_m,  s.all_run_moving_time_s,  s.all_run_elapsed_time_s,  s.all_run_elevation_gain_m,
    s.all_swim_count, s.all_swim_distance_m, s.all_swim_moving_time_s, s.all_swim_elapsed_time_s, s.all_swim_elevation_gain_m,

    -- ytd_*
    s.ytd_ride_count, s.ytd_ride_distance_m, s.ytd_ride_moving_time_s, s.ytd_ride_elapsed_time_s, s.ytd_ride_elevation_gain_m,
    s.ytd_run_count,  s.ytd_run_distance_m,  s.ytd_run_moving_time_s,  s.ytd_run_elapsed_time_s,  s.ytd_run_elevation_gain_m,
    s.ytd_swim_count, s.ytd_swim_distance_m, s.ytd_swim_moving_time_s, s.ytd_swim_elapsed_time_s, s.ytd_swim_elevation_gain_m
  from {{ ref('stg_athlete_stats') }} s
),

-- optional: keep only the latest fetch per athlete per day
dedup_daily as (
  select * except(rn),
         concat(cast(athlete_id as string), '_', cast(snapshot_date as string)) as athlete_id_snapshot_date
  from (
    select src.*,
           row_number() over (partition by athlete_id, snapshot_date order by snapshot_ts desc) as rn
    from src
  )
  where rn = 1
)

-- 👇 FINAL SELECT (required)
select * from dedup_daily
