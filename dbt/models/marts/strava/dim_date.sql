{{ 
  config(
    materialized='table',
    cluster_by=['date_day']
  ) 
}}

{% set start_date = var('dim_date_start', '2024-10-12') %}
{% set end_date   = var('dim_date_end',   '2030-12-31') %}

WITH dates AS (
  SELECT d AS date_day
  FROM UNNEST(GENERATE_DATE_ARRAY(DATE('{{ start_date }}'), DATE('{{ end_date }}'))) AS d
)

SELECT
  -- Surrogate key (common in dimensional modeling)
  CAST(FORMAT_DATE('%Y%m%d', date_day) AS INT64) AS date_key,

  date_day,

  EXTRACT(YEAR FROM date_day) AS year,
  EXTRACT(QUARTER FROM date_day) AS quarter,
  EXTRACT(MONTH FROM date_day) AS month,
  EXTRACT(DAY FROM date_day) AS day_of_month,
  EXTRACT(DAYOFYEAR FROM date_day) AS day_of_year,

  -- ISO attributes
  EXTRACT(ISOYEAR FROM date_day) AS iso_year,
  EXTRACT(ISOWEEK FROM date_day) AS iso_week,
  -- BigQuery: DAYOFWEEK is 1=Sun..7=Sat; convert to ISO 1=Mon..7=Sun
  MOD(EXTRACT(DAYOFWEEK FROM date_day) + 5, 7) + 1 AS iso_day_of_week,

  FORMAT_DATE('%A', date_day) AS day_name,
  FORMAT_DATE('%B', date_day) AS month_name,

  DATE_TRUNC(date_day, WEEK(MONDAY)) AS week_start_date,
  DATE_ADD(DATE_TRUNC(date_day, WEEK(MONDAY)), INTERVAL 6 DAY) AS week_end_date,

  DATE_TRUNC(date_day, MONTH) AS month_start_date,
  DATE_SUB(DATE_ADD(DATE_TRUNC(date_day, MONTH), INTERVAL 1 MONTH), INTERVAL 1 DAY) AS month_end_date,

  DATE_TRUNC(date_day, YEAR) AS year_start_date,
  DATE_SUB(DATE_ADD(DATE_TRUNC(date_day, YEAR), INTERVAL 1 YEAR), INTERVAL 1 DAY) AS year_end_date,

  -- Convenience flags
  (MOD(EXTRACT(DAYOFWEEK FROM date_day) + 5, 7) + 1 IN (6,7)) AS is_weekend,
  (date_day = DATE_TRUNC(date_day, MONTH)) AS is_month_start,
  (date_day = DATE_SUB(DATE_ADD(DATE_TRUNC(date_day, MONTH), INTERVAL 1 MONTH), INTERVAL 1 DAY)) AS is_month_end,
  (date_day = DATE_TRUNC(date_day, YEAR)) AS is_year_start,
  (date_day = DATE_SUB(DATE_ADD(DATE_TRUNC(date_day, YEAR), INTERVAL 1 YEAR), INTERVAL 1 DAY)) AS is_year_end,

  (date_day > CURRENT_DATE()) AS is_future,

  CURRENT_TIMESTAMP() AS mart_loaded_at

FROM dates
