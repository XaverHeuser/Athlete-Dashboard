{% snapshot strava_activities_snapshot %}

{{
  config(
    target_schema='strava_snapshots',
    unique_key='id',
    strategy='check',
    check_cols='all'
  )
}}

select *
from {{ source('strava_data', 'raw_activities') }}

{% endsnapshot %}