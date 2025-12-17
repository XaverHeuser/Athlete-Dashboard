{{ config(materialized='view') }}

WITH base AS (
    SELECT
        SAFE_CAST(activity_id AS INT64) AS activity_id,
        SAFE_CAST(stream_type AS STRING) AS stream_type,
        SAFE_CAST(sequence_index AS INT64) AS sequence_index,
        SAFE_CAST(value_float AS FLOAT64) AS value_float,
        SAFE_CAST(value_int AS INT64) AS value_int,
        SAFE_CAST(value_bool AS BOOL) AS value_bool,
        SAFE_CAST(value_lat AS FLOAT64) AS value_lat,
        SAFE_CAST(value_lng AS FLOAT64) AS value_lng,
        SAFE_CAST(loaded_at AS TIMESTAMP) AS loaded_at
    FROM {{ source('strava_data', 'raw_activity_streams') }}
)

SELECT * FROM base
