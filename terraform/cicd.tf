# Service Account that GitHub Actions will use
resource "google_service_account" "github_actions" {
  account_id   = "github-actions-deployer"
  display_name = "GitHub Actions CI/CD Deployer"
}

# Grant GitHub the ability to build/push Docker images
resource "google_project_iam_member" "ar_writer" {
  project = "finance-analysis-id"
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

# Grant GitHub the ability to trigger Cloud Run Job updates
resource "google_project_iam_member" "cloud_run_developer" {
  project = "finance-analysis-id"
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

# Allow GitHub to pass the runtime service account to Cloud Run
resource "google_project_iam_member" "sa_user" {
  project = "finance-analysis-id"
  role    = "roles/iam.serviceAccountUser"
  member  = "serviceAccount:${google_service_account.github_actions.email}"
}

# ---------------------------------------------------
# Authentication via Workload Identity Federation
# ---------------------------------------------------

# Workload Identity Pool
resource "google_iam_workload_identity_pool" "github_pool" {
  project                   = var.project_id
  workload_identity_pool_id = "github-actions-pool"
  display_name              = "GitHub Actions Pool"
  description               = "Identity pool for GitHub Actions OIDC federation"
}

# Identity Provider targeting GitHub's OIDC issuer
resource "google_iam_workload_identity_pool_provider" "github_provider" {
  project                            = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-actions-provider"
  display_name                       = "GitHub Actions Provider"

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.repository" = "assertion.repository"
    "attribute.owner"      = "assertion.repository_owner"
    "attribute.ref"        = "assertion.ref"
  }
  # Block unauthorized repos AND force it to only accept the main branch globally
  attribute_condition = "assertion.repository == '${var.github_username}/${var.github_repo_name}' && assertion.ref == 'refs/heads/main'"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

# Allow only your specific GitHub repository to impersonate this SA
resource "google_service_account_iam_member" "wif_impersonation" {
  service_account_id = google_service_account.github_actions.name
  role               = "roles/iam.workloadIdentityUser"
  
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/${var.github_username}/${var.github_repo_name}"
}

# Output the Provider Name
output "workload_identity_provider" {
  value = google_iam_workload_identity_pool_provider.github_provider.name
}