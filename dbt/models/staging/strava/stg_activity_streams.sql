{{ config(
    materialized='incremental',
    unique_key='stream_pk',
    on_schema_change='fail',
    partition_by={"field": "ingested_at", "data_type": "timestamp", "granularity": "day"},
    cluster_by=["activity_id", "stream_type"]
) }}

WITH ranked AS (
    SELECT
        SAFE_CAST(activity_id AS INT64) AS activity_id,
        SAFE_CAST(stream_type AS STRING) AS stream_type,
        SAFE_CAST(sequence_index AS INT64) AS sequence_index,

        SAFE_CAST(value_float AS FLOAT64) AS value_float,
        SAFE_CAST(value_int AS INT64) AS value_int,
        SAFE_CAST(value_bool AS BOOL) AS value_bool,
        SAFE_CAST(value_lat AS FLOAT64) AS value_lat,
        SAFE_CAST(value_lng AS FLOAT64) AS value_lng,

        SAFE_CAST(ingested_at AS TIMESTAMP) AS ingested_at,

        CONCAT(
            CAST(activity_id AS STRING), '_',
            stream_type, '_',
            CAST(sequence_index AS STRING)
        ) AS stream_pk,

        ROW_NUMBER() OVER (
            PARTITION BY
                activity_id,
                stream_type,
                sequence_index
            ORDER BY ingested_at DESC
        ) AS rn
    FROM {{ source('strava_data', 'raw_activity_streams') }}
)

select
    activity_id,
    stream_type,
    sequence_index,
    value_float,
    value_int,
    value_bool,
    value_lat,
    value_lng,
    ingested_at,
    stream_pk
FROM ranked
WHERE rn = 1
