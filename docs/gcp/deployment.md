# Deploying a Python Script to Google Cloud Run Jobs Using Docker

This guide explains how to deploy a Python script to Google Cloud Run Jobs using Docker and Google Cloud Build.
It’s ideal for scheduled or on-demand data processing tasks (e.g., ETL jobs, API ingestion, or analytics pipelines).

---

## 1. Prerequisites

Make sure you have:

- A Google Cloud Project with billing enabled
- The Google Cloud CLI (gcloud) installed and authenticated

```bash
gcloud auth login
gcloud config set project PROJECT-ID
```

Enable the required APIs:

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com bigquery.googleapis.com
```

---

## 2. Project Structure

Example layout:

```bash
project/
├── src/
│   ├── main.py
│   ├── ingestion/
│   │   ├── pipelines/strava_pipeline.py
│   │   └── loaders/bigquery_loader.py
│   └── ...
├── requirements.txt
└── Dockerfile
```

Your entry point `(src/main.py)` should contain the logic to run your job.

---

## 3. Create the Dockerfile

In the root directory, create a `Dockerfile`:

```dockerfile
# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Run your script
CMD ['python', 'src/main.py']
```

> Tip: Use `.dockerignore` to exclude unnecessary files (e.g., `.git`, `__pycache__`, etc.) for faster builds.

---

## 4. Create an Artifact Registry for Docker Images

Artifact Registry stores your container images.

```bash
gcloud artifacts repositories create REPO-NAME \
  --repository-format=docker \
  --location=REGION \
  --description="Docker repo for Cloud Run Jobs"
```

Example:

```bash
gcloud artifacts repositories create cloudrun-jobs \
  --repository-format=docker \
  --location=europe-west1 \
  --description="Docker repo for Cloud Run Jobs"
```

---

## 5. Build and Push Your Docker Image

### Build and push directly with Cloud Build

```bash
gcloud builds submit \
  --tag REGION-docker.pkg.dev/PROJECT_ID/REPO-NAME/DOCKER-JOB-NAME:latest
```

Example:

```bash
gcloud builds submit \
  --tag europe-west1-docker.pkg.dev/my-project/cloudrun-jobs/athlete-job:latest
```

### Optional: Build & Push Locally

If you prefer local Docker builds:

```bash
docker build -t europe-west1-docker.pkg.dev/PROJECT_ID/REPO_NAME/dbt-job:latest .
docker push europe-west1-docker.pkg.dev/PROJECT_ID/REPO_NAME/dbt-job:latest
```

Then update the job to use the new image:

```bash
gcloud run jobs update dbt-job \
  --image=europe-west1-docker.pkg.dev/PROJECT_ID/REPO_NAME/dbt-job:latest \
  --region=europe-west1
```

### Build and Push with different Dockerfile

Local:

```bash
docker build -f Dockerfile.dbt -t europe-west1-docker.pkg.dev/athlete-dashboard-467718/athlete-dashboard/dbt-job:latest .
docker push europe-west1-docker.pkg.dev/athlete-dashboard-467718/athlete-dashboard/dbt-job:latest 
```

Or create cloudbuild.yaml:

```yaml
steps:
  - name: gcr.io/cloud-builders/docker
    args: ['build',
           '-t', 'europe-west1-docker.pkg.dev/athlete-dashboard-467718/athlete-dashboard/dbt-job:latest',
           '-f', 'Dockerfile.dbt',
           '.']
images:
  - 'europe-west1-docker.pkg.dev/athlete-dashboard-467718/athlete-dashboard/dbt-job:latest'
```

Build image with yaml:

```bash
gcloud builds submit --config cloudbuild.yaml .
```

Then update the job to use the new image:

```bash
gcloud run jobs update dbt-job --image=europe-west1-docker.pkg.dev/athlete-dashboard-467718/athlete-dashboard/dbt-job:latest --region=europe-west1 
```

*If you change your code later, rerun this command to build and push an updated image.*

---

## 6. Grant Permissions (One-Time Setup)

Cloud Run Jobs and Cloud Build need permissions to access Artifact Registry, Cloud Storage, and BigQuery.

### Cloud Build & Compute Engine Access

```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/storage.admin" \
  --condition=None

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/storage.admin" \
  --condition=None
```

### BigQuery Access for the Job Runtime

```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/bigquery.jobUser" \
  --condition=None

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor" \
  --condition=None
```

---

## 7. Deploy the Cloud Run Job

Create the job (only once):

```bash
gcloud run jobs create JOB-NAME \
  --image REGION-docker.pkg.dev/PROJECT_ID/REPO-NAME/DOCKER-JOB-NAME:latest \
  --region REGION
```

---

## 8. Run the Job

Run your script on demand:

```bash
gcloud run jobs execute JOB-NAME --region REGION
```

Check job status and logs:

```bash
gcloud run jobs executions list --region REGION
gcloud run jobs executions describe [EXECUTION_NAME] --region REGION
```

*Logs also appear in Cloud Console → Logging → Logs Explorer.*

---

## 9. Updating Code Later

When you modify your Python code:

```bash
# Rebuild and push the new image
gcloud builds submit \
  --tag REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME/JOB_NAME:latest

# Update the Cloud Run Job to use the new image
gcloud run jobs update JOB_NAME \
  --image REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME/JOB_NAME:latest \
  --region REGION

# (Optional) Run immediately
gcloud run jobs execute JOB_NAME --region REGION
```

---

## 10. Schedule the Job

Run your script automatically using Cloud Scheduler:

```bash
gcloud scheduler jobs create http JOB-NAME-schedule \
  --schedule="0 3 * * *" \
  --uri="$(gcloud run jobs describe JOB-NAME --region REGION --format='value(latestCreatedExecution.uri)')" \
  --http-method=POST \
  --oidc-service-account-email="PROJECT_NUMBER-compute@developer.gserviceaccount.com"
```

---

## Summary

| Action                       | Command                                                  |
| ---------------------------- | -------------------------------------------------------- |
| **Build image**              | `gcloud builds submit --tag <artifact-url>`              |
| **Deploy job**               | `gcloud run jobs create JOB_NAME --image <artifact-url>` |
| **Run job manually**         | `gcloud run jobs execute JOB_NAME`                       |
| **Update after code change** | Rebuild → `gcloud run jobs update JOB_NAME`              |
| **Check logs**               | `gcloud run jobs executions list / describe`             |

---

## Best Practices

- Use specific image tags (e.g., :v1.0.0) for reproducibility.
- Keep dependencies pinned in requirements.txt.
- Store secrets in Secret Manager, not environment variables.
- Use Cloud Build triggers to automate image deployment from Git commits.

## Important addition

Due to changes in GCP's IAM, the right management is different. Therefore, the deployment is different.
The following commands are now used to build docker images with gcloud

- gcloud builds submit --project athlete-dashboard-467718  --gcs-source-staging-dir=gs://athlete-dashboard-467718-cloudbuild-eu/source  --config cloudbuild.dbt.yaml .
- gcloud builds submit --project athlete-dashboard-467718   --gcs-source-staging-dir=gs://athlete-dashboard-467718-cloudbuild-eu/source   --config cloudbuild.el.yaml .
