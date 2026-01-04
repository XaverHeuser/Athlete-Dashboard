{{ config(materialized='view') }}

with base AS (
    SELECT
        -- Identifiers
        SAFE_CAST(id AS INT64) AS athlete_id,

        SAFE_CAST(username AS STRING) AS username,
        SAFE_CAST(firstname AS STRING) AS firstname,
        SAFE_CAST(lastname AS STRING) AS lastname,
        SAFE_CAST(bio AS STRING) AS bio,
        SAFE_CAST(city AS STRING) AS city,
        SAFE_CAST(state AS STRING) AS state,
        SAFE_CAST(country AS STRING) AS country,
        SAFE_CAST(sex AS STRING) AS sex,
        SAFE_CAST(premium AS BOOL) AS has_premium,
        SAFE_CAST(summit AS BOOL) AS has_summit,
        SAFE_CAST(badge_type_id AS INT64) AS badge_type_id,
        SAFE_CAST(weight AS FLOAT64) AS weight_kg,
        SAFE_CAST(profile_medium AS STRING) AS profile_medium,
        SAFE_CAST(profile AS STRING) AS profile,
        friend,
        follower,

        -- Timestamps
        SAFE_CAST(created_at AS TIMESTAMP) AS created_at,
        SAFE_CAST(updated_at AS TIMESTAMP) AS updated_at,

        -- Metadata
        SAFE_CAST(resource_state AS INT64) AS resource_state,
        SAFE_CAST(ingested_at AS TIMESTAMP) AS ingested_at,
        CURRENT_TIMESTAMP() AS processed_at

    FROM {{ source('strava_data', 'raw_athlete_info') }}
)

SELECT * FROM base
