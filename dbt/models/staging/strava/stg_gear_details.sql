{{ config(
    materialized='incremental',
    unique_key='gear_id',
    on_schema_change='fail'
) }}

WITH ranked AS (
    SELECT
        SAFE_CAST(id AS STRING) AS gear_id,
        SAFE_CAST(name AS STRING) AS name,
        SAFE_CAST(nickname AS STRING) AS nickname,
        SAFE_CAST(primary AS BOOL) AS is_primary,
        SAFE_CAST(retired AS BOOL) AS is_retired,
        SAFE_CAST(distance AS INT64) AS distance_m,
        SAFE_CAST(converted_distance AS FLOAT64) AS distance_km,
        SAFE_CAST(brand_name AS STRING) AS brand_name,
        SAFE_CAST(model_name AS STRING) AS model_name,
        SAFE_CAST(frame_type AS INT64) AS frame_type,
        SAFE_CAST(description AS STRING) AS description,
        SAFE_CAST(weight AS FLOAT64) AS weight_kg,
        SAFE_CAST(notification_distance AS FLOAT64) AS notification_distance_km,
        SAFE_CAST(ingested_at AS TIMESTAMP) AS ingested_at,
        CURRENT_TIMESTAMP() AS processed_at,

        ROW_NUMBER() OVER (
            PARTITION BY id
            ORDER BY ingested_at DESC
        ) AS rn
    FROM {{ source('strava_data', 'raw_gear_details') }}
)

SELECT
    gear_id,
    name,
    nickname,
    is_primary,
    is_retired,
    distance_m,
    distance_km,
    brand_name,
    model_name,
    frame_type,
    description,
    weight_kg,
    notification_distance_km,
    ingested_at,
    processed_at
FROM ranked
WHERE rn = 1
