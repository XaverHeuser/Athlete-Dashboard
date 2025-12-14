{{ config(materialized='table') }}

SELECT
  d AS date,
  EXTRACT(YEAR FROM d) AS year,
  EXTRACT(MONTH FROM d) AS month,
  EXTRACT(ISOWEEK FROM d) AS iso_week,
  DATE_TRUNC(d, WEEK(MONDAY)) AS week_start,
  DATE_TRUNC(d, MONTH) AS month_start,
  DATE_TRUNC(d, YEAR) AS year_start
FROM UNNEST(
  GENERATE_DATE_ARRAY('2024-10-12', '2030-12-31')
) AS d
