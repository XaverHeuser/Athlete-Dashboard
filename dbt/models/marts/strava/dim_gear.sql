{{
  config(
    materialized='table',
    cluster_by=['gear_type', 'gear_id']
  )
}}

WITH src AS (
  SELECT
    gear_id,
    frame_type AS frame_type_code,

    NULLIF(TRIM(name), '') AS name,
    NULLIF(TRIM(nickname), '') AS nickname,
    CAST(is_primary AS BOOL) AS is_primary,
    CAST(is_retired AS BOOL) AS is_retired,

    NULLIF(TRIM(brand_name), '') AS brand_name,
    NULLIF(TRIM(model_name), '') AS model_name,
    description,

    CAST(weight_kg AS FLOAT64) AS weight_kg,

    CAST(distance_m AS FLOAT64) AS distance_m,
    -- Prefer a single source of truth: compute km from meters
    SAFE_DIVIDE(CAST(distance_m AS FLOAT64), 1000.0) AS distance_km,

    CAST(notification_distance_km AS FLOAT64) AS notification_distance_km

  FROM {{ ref('stg_gear_details') }}
  WHERE gear_id IS NOT NULL
),

derived AS (
  SELECT
    gear_id,

    CASE
      WHEN LOWER(SUBSTR(gear_id, 1, 1)) = 'b' THEN 'Bike'
      WHEN LOWER(SUBSTR(gear_id, 1, 1)) = 'g' THEN 'Shoes'
      ELSE 'Other'
    END AS gear_type,

    CASE
      WHEN LOWER(SUBSTR(gear_id, 1, 1)) = 'b' THEN
        CASE frame_type_code
          WHEN 1 THEN 'Mountain Bike'
          WHEN 2 THEN 'Cyclocross Bike'
          WHEN 3 THEN 'Road Bike'
          WHEN 4 THEN 'Time Trial Bike'
          WHEN 5 THEN 'Gravel Bike'
          ELSE 'Other'
        END
      ELSE NULL
    END AS frame_type,

    name,
    nickname,
    is_primary,
    is_retired,
    brand_name,
    model_name,
    description,
    weight_kg,
    distance_m,
    distance_km,

    -- Parse "+ 123km" or "+123.4 km" or "+123,4km"
    COALESCE(
      SAFE_CAST(
        REPLACE(
          REGEXP_EXTRACT(description, r'\+\s*([\d]+(?:[.,]\d+)?)\s*km'),
          ',',
          '.'
        ) AS FLOAT64
      ),
      0.0
    ) AS additional_distance_km,

    notification_distance_km

  FROM src
),

final AS (
  SELECT
    gear_id,
    gear_type,
    frame_type,
    name,
    nickname,
    is_primary,
    is_retired,
    brand_name,
    model_name,
    description,
    weight_kg,
    distance_m,
    distance_km,
    additional_distance_km,
    (distance_km + additional_distance_km) AS total_distance_km,
    notification_distance_km,
    (additional_distance_km > 0) AS has_additional_distance_in_description,
    CURRENT_TIMESTAMP() AS mart_loaded_at
  FROM derived
)

SELECT * FROM final
