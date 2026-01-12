{{ config(materialized='table') }}

WITH meta AS (
  SELECT CURRENT_TIMESTAMP() AS mart_loaded_at
)
SELECT discipline, meta.mart_loaded_at
FROM meta
CROSS JOIN UNNEST(['Run','Ride','Swim','Strength']) AS discipline
