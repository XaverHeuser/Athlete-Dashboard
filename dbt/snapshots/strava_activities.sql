{% snapshot strava_activities_snapshot %}

{{
  config(
    target_schema='strava_snapshots',
    unique_key='id',
    strategy='check',
    check_cols=[
      'activity_name',
      'sport_type',
      'workout_type',
      'distance_m',
      'moving_time_s',
      'elapsed_time_s',
      'elevation_gain_m',
      'start_date_utc',
      'start_date_local',
      'timezone',
      'utc_offset_s',
      'is_trainer',
      'is_commute',
      'is_manual',
      'is_flagged',
      'has_heartrate',
      'is_private',
      'visibility',
      'achievement_count',
      'kudos_count',
      'comment_count',
      'athlete_count',
      'photo_count'
    ]
  )
}}

-- We select a stable, scalar view of each activity.
-- No arrays, no structs, nothing BigQuery can't diff.
select
    -- Identity
    SAFE_CAST(id AS INT64)                         AS id,
    SAFE_CAST(athlete.id AS INT64)                 AS athlete_id,

    -- Basic info / core metrics
    SAFE_CAST(name AS STRING)                      AS activity_name,
    SAFE_CAST(sport_type AS STRING)                AS sport_type,
    SAFE_CAST(workout_type AS INT64)               AS workout_type,
    SAFE_CAST(distance AS FLOAT64)                 AS distance_m,
    SAFE_CAST(moving_time AS INT64)                AS moving_time_s,
    SAFE_CAST(elapsed_time AS INT64)               AS elapsed_time_s,
    SAFE_CAST(total_elevation_gain AS FLOAT64)     AS elevation_gain_m,

    -- Timing
    TIMESTAMP(start_date)                          AS start_date_utc,
    TIMESTAMP(start_date_local)                    AS start_date_local,
    SAFE_CAST(timezone AS STRING)                  AS timezone,
    SAFE_CAST(utc_offset AS INT64)                 AS utc_offset_s,

    -- Engagement / social
    SAFE_CAST(achievement_count AS INT64)          AS achievement_count,
    SAFE_CAST(kudos_count AS INT64)                AS kudos_count,
    SAFE_CAST(comment_count AS INT64)              AS comment_count,
    SAFE_CAST(athlete_count AS INT64)              AS athlete_count,
    SAFE_CAST(photo_count AS INT64)                AS photo_count,

    -- Flags
    SAFE_CAST(trainer AS BOOL)                     AS is_trainer,
    SAFE_CAST(commute AS BOOL)                     AS is_commute,
    SAFE_CAST(manual AS BOOL)                      AS is_manual,
    SAFE_CAST(flagged AS BOOL)                     AS is_flagged,
    SAFE_CAST(has_heartrate AS BOOL)               AS has_heartrate,
    SAFE_CAST(private AS BOOL)                     AS is_private,
    SAFE_CAST(visibility AS STRING)                AS visibility,

    -- Lineage / traceability
    SAFE_CAST(upload_id AS INT64)                  AS upload_id,
    SAFE_CAST(upload_id_str AS STRING)             AS upload_id_str,
    SAFE_CAST(external_id AS STRING)               AS external_id,

    CURRENT_TIMESTAMP()                            AS _staged_at

from {{ source('strava_data', 'raw_activities') }}

{% endsnapshot %}