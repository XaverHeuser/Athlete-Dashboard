variable "project_id" {
  description = "The ID of the project in which to create the resources."
  type        = string
  default     = "athlete-dashboard1"
}

variable "region" {
  description = "The region in which to create the resources."
  type        = string
  default     = "europe-west1"
}

variable "artifact_registry_repo_el_name" {
  description = "The name of the Artifact Registry repository to create for storing Docker images."
  type        = string
  default     = "athlete-dashboard-el-repo"
}

variable "artifact_registry_repo_dbt_name" {
  description = "The name of the Artifact Registry repository to create for storing Docker images."
  type        = string
  default     = "athlete-dashboard-dbt-repo"
}

# -----------------------
# BigQuery Datasets ids
# -----------------------
variable "dataset_raw_id" {
  description = "The dataset ID for the raw BigQuery dataset."
  type        = string
  default     = "dataset_raw"
}

variable "dataset_staging_id" {
  description = "The dataset ID for the staging BigQuery dataset."
  type        = string
  default     = "dataset_staging"
}

variable "dataset_intermediate_id" {
  description = "The dataset ID for the intermediate BigQuery dataset."
  type        = string
  default     = "dataset_intermediate"
}

variable "dataset_mart_id" {
  description = "The dataset ID for the mart BigQuery dataset."
  type        = string
  default     = "dataset_mart"
}

variable "github_username" {
  description = "GitHub username for OIDC federation."
  type        = string
  default     = "XaverHeuser"
}

variable "github_repo_name" {
  description = "GitHub repository name for OIDC federation."
  type        = string
  default     = "Athlete-Dashboard"
}