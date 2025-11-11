{{ config(materialized='table') }}

WITH base AS (
    SELECT
        athlete_id,
        INITCAP(firstname) AS firstname,
        INITCAP(lastname) AS lastname,
        COALESCE(username, '') AS username,
        COALESCE(bio, '') AS bio,
        COALESCE(city, 'Unknown') AS city,
        COALESCE(state, 'Unknown') AS state,
        COALESCE(country, 'Unknown') AS country,
        sex,
        CASE WHEN has_premium OR has_summit THEN TRUE ELSE FALSE END AS is_premium_user,
        ROUND(weight_kg, 1) AS weight_kg,
        profile_medium AS profile_medium_img_url,
        profile AS profile_img_url,
        created_at
    FROM {{ ref('stg_athlete_info') }}
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
