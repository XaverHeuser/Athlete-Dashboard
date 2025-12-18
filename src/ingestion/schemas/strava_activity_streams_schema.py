from google.cloud import bigquery

ACTIVITY_STREAMS_SCHEMA = [
    bigquery.SchemaField('activity_id', 'INT64'),
    bigquery.SchemaField('stream_type', 'STRING'),
    bigquery.SchemaField('sequence_index', 'INT64'),
    bigquery.SchemaField('value_float', 'FLOAT64'),
    bigquery.SchemaField('value_int', 'INT64'),
    bigquery.SchemaField('value_bool', 'BOOL'),
    bigquery.SchemaField('value_lat', 'FLOAT64'),
    bigquery.SchemaField('value_lng', 'FLOAT64'),
    bigquery.SchemaField('ingested_at', 'TIMESTAMP'),
]
