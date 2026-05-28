resource "google_service_account" "el_job_sa" {
  account_id   = "el-pipeline-sa"
  display_name = "Service Account for Extract & Load Pipeline"
}

resource "google_project_iam_member" "el_job_sa_bigquery_jobuser" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.el_job_sa.email}"
}

resource "google_bigquery_dataset_iam_member" "el_dataset_raw_editor" {
  dataset_id = var.dataset_raw_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.el_job_sa.email}"
}

resource "google_cloud_run_v2_job" "el_job" {
  name                = "extract-load-job"
  location            = var.region
  deletion_protection = false

  labels = {
    Service     = "extract-load"
    Environment = "prod"
  }

  template {
    template {
      service_account = google_service_account.el_job_sa.email
      timeout         = "3600s"
      max_retries     = 1

      containers {
        image = "us-docker.pkg.dev/cloudrun/container/hello:latest"
        env {
          name  = "GCP_PROJECT_ID"
          value = var.project_id
        }
        env {
          name  = "GCP_REGION"
          value = var.region
        }
        env {
          name  = "RAW_DATASET"
          value = var.dataset_raw_id
        }

        env {
          name  = "CLOUD_RUN_DBT_JOB_NAME"
          value = google_cloud_run_v2_job.dbt_job.name
        }

        # Dynamically inject the runtime secret variables configured in Secret Manager
        dynamic "env" {
          for_each = toset(var.strava_api_secrets)
          content {
            name = env.key
            value_source {
              secret_key_ref {
                secret  = google_secret_manager_secret.secrets[env.key].id
                version = "latest"
              }
            }
          }
        }
      }
    }
  }

  depends_on = [
    google_project_service.run_api,
    google_artifact_registry_repository.el_image_repo,
    google_secret_manager_secret.secrets,
    google_secret_manager_secret_iam_member.job_sa_secret_access,
    google_bigquery_dataset_iam_member.el_dataset_raw_editor
  ]
}

# Inter-pipeline chaining permission: Allows the EL Container code to trigger execution of the dbt Job
resource "google_project_iam_member" "el_can_trigger_dbt" {
  project = var.project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.el_job_sa.email}"
}