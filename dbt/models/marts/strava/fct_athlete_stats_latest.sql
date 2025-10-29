-- models/marts/strava/fct_athlete_stats_latest.sql
{{ config(materialized='view') }}

with ranked as (
  select f.*,
         row_number() over (partition by athlete_id order by snapshot_ts desc) as rn
  from {{ ref('fct_athlete_stats_snapshot') }} f
)
select * from ranked where rn = 1
