resource "google_service_account" "dbt_job_sa" {
  account_id   = "dbt-pipeline-sa"
  display_name = "Service Account for the dbt Transform Pipeline"
}

resource "google_project_iam_member" "dbt_bq_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.dbt_job_sa.email}"
}

resource "google_cloud_run_v2_job" "dbt_job" {
  name                = "dbt-transform-job"
  location            = var.region
  deletion_protection = false

  template {
    template {
      service_account = google_service_account.dbt_job_sa.email
      timeout         = "3600s"
      max_retries     = 1

      containers {
        image = "us-docker.pkg.dev/cloudrun/container/hello:latest"
      }
    }
  }
  depends_on = [
    google_project_service.run_api,
    google_artifact_registry_repository.dbt_image_repo,
    google_project_iam_member.dbt_bq_admin
  ]
}