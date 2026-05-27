resource "google_bigquery_dataset" "dataset_raw" {
  dataset_id = var.dataset_raw_id
}

resource "google_bigquery_dataset" "dataset_staging" {
  dataset_id = var.dataset_staging_id
}

resource "google_bigquery_dataset" "dataset_intermediate" {
  dataset_id = var.dataset_intermediate_id
}

resource "google_bigquery_dataset" "dataset_mart" {
  dataset_id = var.dataset_mart_id
}