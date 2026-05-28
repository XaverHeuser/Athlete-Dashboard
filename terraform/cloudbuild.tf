resource "google_artifact_registry_repository" "el_image_repo" {
  location      = var.region
  repository_id = var.artifact_registry_repo_el_name
  description   = "Artifact Registry repository for storing Docker images used for el pipeline"
  format        = "DOCKER"

  labels = {
    service     = "artifactregistry-repositories"
    environment = "prod"
  }

  depends_on = [google_project_service.artifactregistry_api]
}

resource "google_artifact_registry_repository" "dbt_image_repo" {
  location      = var.region
  repository_id = var.artifact_registry_repo_dbt_name
  description   = "Artifact Registry repository for storing Docker images used for dbt pipeline"
  format        = "DOCKER"

  labels = {
    service     = "artifactregistry-repositories"
    environment = "prod"
  }

  depends_on = [google_project_service.artifactregistry_api]
}

# Check the need for this bucket
resource "google_storage_bucket" "cloudbuild_bucket" {
  name          = "${var.project_id}_cloudbuild"
  location      = var.region
  force_destroy = true # Allow bucket deletion even if it contains objects

  labels = {
    service     = "cloudbuild"
    environment = "prod"
  }
}

resource "google_service_account" "sa-cloudbuild-runner" {
  account_id   = "cloudbuild-runner-sa"
  display_name = "Service Account utilized by Cloud Build Pipelines"
}

resource "google_project_iam_member" "cloudbuild_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.sa-cloudbuild-runner.email}"
}

resource "google_project_iam_member" "cloudbuild_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.sa-cloudbuild-runner.email}"
}

# Grant Cloud Logging permissions so it can write build logs
resource "google_project_iam_member" "cloudbuild_logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.sa-cloudbuild-runner.email}"
}

# Grant Artifact Registry Writer permissions so it can push the Docker image
resource "google_project_iam_member" "cloudbuild_artifact_registry_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.sa-cloudbuild-runner.email}"
}

# Grant Cloud Build Worker permissions so it can physically execute the job steps
resource "google_project_iam_member" "cloudbuild_worker" {
  project = var.project_id
  role    = "roles/cloudbuild.builds.builder"
  member  = "serviceAccount:${google_service_account.sa-cloudbuild-runner.email}"
}