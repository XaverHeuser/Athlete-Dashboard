{{ config(materialized='table') }}

WITH base AS (
    SELECT
        gear_id,

        -- Determine gear type based on gear_id prefix
        CASE
            WHEN LEFT(gear_id, 1) = 'b' THEN 'Bike'
            WHEN LEFT(gear_id, 1) = 'g' THEN 'Shoes'
            ELSE 'Other'
        END AS gear_type,

        -- Frame type mapping
        CASE frame_type
            WHEN 1 THEN 'Mountain Bike'
            WHEN 2 THEN 'Cyclocross Bike'
            WHEN 3 THEN 'Road Bike'
            WHEN 4 THEN 'Time Trial Bike'
            WHEN 5 THEN 'Gravel Bike'
            ELSE 'Other'
        END AS frame_type,

        -- Gear details
        name,
        nickname,
        is_primary,
        is_retired,
        brand_name,
        model_name,
        description,
        weight_kg,

        -- Base distances
        distance_m,
        distance_km,
        
        -- Total distance calculation (including additional distances mentioned in description)
        distance_km
        + COALESCE(
            SAFE_CAST(
                REPLACE(
                    REGEXP_EXTRACT(description, r'\+\s*([\d,]+)km'),
                    ',',
                    '.'
                ) AS FLOAT64
            ),
            0
        ) AS total_distance_km,
        notification_distance_km,

        CURRENT_TIMESTAMP() AS mart_loaded_at

    FROM {{ ref('stg_gear_details') }}
)

SELECT * FROM base
