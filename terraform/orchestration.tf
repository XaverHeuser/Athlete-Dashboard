resource "google_service_account" "scheduler_sa" {
  account_id   = "cloud-scheduler-sa"
  display_name = "Service Account for Cloud Scheduler Trigger"
}

# Gives scheduler credentials access rights to kick off standard Cloud Run jobs
resource "google_project_iam_member" "scheduler_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.scheduler_sa.email}"
}

# Cron Job triggering el-job
resource "google_cloud_scheduler_job" "el_job_trigger" {
  name             = "el-job-trigger"
  description      = "Triggers the el-job every day at 9am Berlin time"
  schedule         = "0 9 * * *"
  time_zone        = "Europe/Berlin"
  attempt_deadline = "320s"

  retry_config {
    retry_count = 1
  }

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.el_job.name}:run"

    oauth_token {
      service_account_email = google_service_account.scheduler_sa.email
    }
  }
  depends_on = [google_project_service.scheduler_api]
}