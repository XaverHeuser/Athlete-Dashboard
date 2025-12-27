{{ config(materialized='table') }}

WITH base AS (
    SELECT
        athlete_id,
        firstname,
        lastname,

        NULLIF(username, '') AS username,
        NULLIF(bio, '') AS bio,

        COALESCE(city, 'Unknown') AS city,
        COALESCE(state, 'Unknown') AS state,
        COALESCE(country, 'Unknown') AS country,

        sex,
        
        (COALESCE(has_premium, FALSE) OR COALESCE(has_summit, FALSE)) AS is_premium_user,

        ROUND(weight_kg, 1) AS weight_kg,

        profile_medium AS profile_medium_img_url,
        profile AS profile_img_url,

        CAST(created_at AS TIMESTAMP) AS created_at

    FROM {{ ref('stg_athlete_info') }}
    WHERE athlete_id IS NOT NULL
),

activity_summary AS (
    SELECT
        athlete_id,
        MIN(start_date_local) AS first_activity_date,
        MAX(start_date_local) AS last_activity_date,
        COUNT(*) AS total_activities
    FROM {{ ref('stg_activities') }}
    
    GROUP BY 1
)

SELECT
    b.*,
    a.first_activity_date,
    a.last_activity_date,
    a.total_activities,
    CURRENT_TIMESTAMP() AS mart_loaded_at
FROM base b
LEFT JOIN activity_summary a USING (athlete_id)
