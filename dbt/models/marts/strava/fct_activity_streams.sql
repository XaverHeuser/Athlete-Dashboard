{{config(materialized='table')}}

SELECT
    activity_id,
    sequence_index,

    MAX(CASE WHEN stream_type = 'time' THEN value_int END) AS time_s,
    MAX(CASE WHEN stream_type = 'distance' THEN value_float END) AS distance_m,
    MAX(CASE WHEN stream_type = 'heartrate' THEN value_int END) AS heartrate_bpm,
    MAX(CASE WHEN stream_type = 'velocity_smooth' THEN value_float END) AS velocity_smooth_mps,
    MAX(CASE WHEN stream_type = 'altitude' THEN value_float END) AS altitude_m,
    MAX(CASE WHEN stream_type = 'cadence' THEN value_int END) AS cadence_rpm,
    MAX(CASE WHEN stream_type = 'moving' THEN value_bool END) AS moving,
    MAX(CASE WHEN stream_type = 'watts' THEN value_int END) AS power_w,
    MAX(CASE WHEN stream_type = 'temp' THEN value_int END) AS temp_c,
    MAX(CASE WHEN stream_type = 'grade_smooth' THEN value_float END) AS grade_smooth_pct,
    MAX(value_lat) as lat,
    MAX(value_lng) as lng,

    CURRENT_TIMESTAMP() AS _mart_loaded_at

FROM {{ ref('stg_activity_streams') }}
GROUP BY activity_id, sequence_index
ORDER BY activity_id, sequence_index
