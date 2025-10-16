"""Settings for different tools."""

DATA_SOURCE = 'strava'  # Options: 'strava', 'garmin'
DATA_STORAGE = 'bigquery'  # Options: 'bigquery', 'postgres'

# --- Google Cloud Platform (GCP) Configuration ---
GCP_PROJECT_ID = 'athlete-dashboard-467718'
BIGQUERY_DATASET = 'strava_data'
BIGQUERY_RAW_TABLE = 'strava_data_raw'
