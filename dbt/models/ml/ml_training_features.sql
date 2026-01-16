{{
  config(
    materialized='table',
    cluster_by=['athlete_id', 'discipline', 'training_bucket_start'],
    tags=['ml', 'training']
  )
}}

-- TODO: Test in notebook -> When ready, implement model here
