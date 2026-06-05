resource "google_service_account" "airflow_local_dev" {
  account_id   = "airflow-local-dev"
  display_name = "Local Airflow Dev Service Account"
}

resource "google_project_iam_member" "cloud_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.airflow_local_dev.email}"
}

resource "google_project_iam_member" "cloud_run_viewer" {
  project = var.project_id
  role    = "roles/run.viewer"
  member  = "serviceAccount:${google_service_account.airflow_local_dev.email}"
}