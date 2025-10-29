{{ config(materialized='table') }}

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
    created_at,
    CURRENT_TIMESTAMP() AS mart_loaded_at
FROM {{ ref('stg_athlete_info') }}
