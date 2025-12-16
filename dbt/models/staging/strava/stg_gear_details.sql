{{ config(materialized = 'view') }}

WITH base AS (
    SELECT
        -- Identifiers
        SAFE_CAST(id AS STRING) AS gear_id,

        -- Gear details
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
        
        -- Metadata
        CURRENT_TIMESTAMP() AS _staged_at

    FROM {{ source('strava_data', 'raw_gear_details') }}
)

SELECT * FROM base
