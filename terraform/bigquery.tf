resource "google_bigquery_dataset" "dataset_raw" {
  dataset_id = var.dataset_raw_id
  location   = var.region
  labels = {
    service     = "bigquery-datasets"
    environment = "prod"
    data_stage  = "raw"
  }
}

resource "google_bigquery_dataset" "dataset_staging" {
  dataset_id = var.dataset_staging_id
  location   = var.region
  labels = {
    service     = "bigquery-datasets"
    environment = "prod"
    data_stage  = "staging"
  }
}

resource "google_bigquery_dataset" "dataset_intermediate" {
  dataset_id = var.dataset_intermediate_id
  location   = var.region
  labels = {
    service     = "bigquery-datasets"
    environment = "prod"
    data_stage  = "intermediate"
  }
}

resource "google_bigquery_dataset" "dataset_mart" {
  dataset_id = var.dataset_mart_id
  location   = var.region
  labels = {
    service     = "bigquery-datasets"
    environment = "prod"
    data_stage  = "mart"
  }
}