{{ config(
    materialized='incremental',
    unique_key=['athlete_id', 'snapshot_date', 'sport', 'period'],
    partition_by={
        "field": "snapshot_date",
        "data_type": "date"
    },
    on_schema_change='fail'
) }}

with base as (

    select *
    from {{ ref('stg_athlete_stats') }}

    {% if is_incremental() %}
        where snapshot_date >= date_sub(current_date(), interval 2 day)
    {% endif %}

),

unpivoted as (

    -- RIDE / RECENT
    select
        athlete_id,
        snapshot_date,
        fetched_at as snapshot_ts,
        'ride' as sport,
        'recent' as period,
        recent_ride_count as activity_count,
        recent_ride_distance_m as distance_m,
        recent_ride_moving_time_s as moving_time_s,
        recent_ride_elapsed_time_s as elapsed_time_s,
        recent_ride_elevation_gain_m as elevation_gain_m,
        recent_ride_achievement_count as achievement_count
    from base

    union all

    -- RUN / RECENT
    select
        athlete_id,
        snapshot_date,
        fetched_at,
        'run',
        'recent',
        recent_run_count,
        recent_run_distance_m,
        recent_run_moving_time_s,
        recent_run_elapsed_time_s,
        recent_run_elevation_gain_m,
        recent_run_achievement_count
    from base

    union all

    -- SWIM / RECENT
    select
        athlete_id,
        snapshot_date,
        fetched_at,
        'swim',
        'recent',
        recent_swim_count,
        recent_swim_distance_m,
        recent_swim_moving_time_s,
        recent_swim_elapsed_time_s,
        recent_swim_elevation_gain_m,
        recent_swim_achievement_count
    from base
)

select
    *,
    SAFE_DIVIDE(distance_m, moving_time_s) AS avg_speed_m_per_s,
    SAFE_DIVIDE(elevation_gain_m, distance_m / 1000) AS elevation_gain_per_km,
    CURRENT_TIMESTAMP() AS _mart_loaded_at
from unpivoted
