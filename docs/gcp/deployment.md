# Deploying a Python Script to Google Cloud Run Jobs Using Docker

This guide explains how to deploy a Python script to Google Cloud Run Jobs using Docker and Google Cloud Build.

## 1. Prerequisites

Make sure you have:

- A Google Cloud Project
- The gcloud CLI installed and authenticated

```bash
gcloud auth login
gcloud config set project PROJECT-ID
```

- Billing enabled
- APIs enabled:

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com bigquery.googleapis.com
```

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

## 3. Create the Dockerfile

In the root directory, create a Dockerfile:

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
CMD ["python", "src/main.py"]
```

## 4. Create an Artifact Registry for Docker Images

Create the repository once (replace region if needed):

```bash
gcloud artifacts repositories create REPO-NAME \
  --repository-format=docker \
  --location=REGION \
  --description="Docker repo for Cloud Run Jobs"
```

## 5. Build and Push Your Docker Image

Run this command from your project root:

```bash
gcloud builds submit \
  --tag REGION-docker.pkg.dev/PROJECT_ID/REPO-NAME/DOCKER-JOB-NAME:latest
```

This:
- Builds your Docker image using your local Dockerfile
- Pushes it to Google Artifact Registry

*If you change your code later, rerun this command to build and push an updated image.*

## 6. Grant Permissions (One-Time Setup)

**Grant Cloud Build and Compute Engine access to Storage & Artifact Registry**

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

**Grant BigQuery permissions for the job runtime**
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
*(These enable the job to load data into BigQuery.)*

## 7. Deploy the Cloud Run Job

Create the job (only once):

```bash
gcloud run jobs create JOB-NAME \
  --image REGION-docker.pkg.dev/PROJECT_ID/REPO-NAME/DOCKER-JOB-NAME:latest \
  --region REGION
```

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

## 9. Updating Code Later

When you change your Python code:

```bash
# Rebuild and push
gcloud builds submit \
  --tag REGION-docker.pkg.dev/PROJECT_ID/REPO-NAME/DOCKER_PACKAGE-NAME:latest

# Redeploy the job to use the new image
gcloud run jobs update JOB-NAME \
  --image REGION-docker.pkg.dev/PROJECT_ID/REPO-NAME/DOCKER_PACKAGE-NAME:latest \
  --region REGION
```

## 10. Schedule the Job

Run your script automatically using Cloud Scheduler:

```bash
gcloud scheduler jobs create http JOB-NAME-schedule \
  --schedule="0 3 * * *" \
  --uri="$(gcloud run jobs describe JOB-NAME --region REGION --format='value(latestCreatedExecution.uri)')" \
  --http-method=POST \
  --oidc-service-account-email="PROJECT_NUMBER-compute@developer.gserviceaccount.com"
```

## Summary

| Step  | Command |
|-------|---------|
| Build image	                  | gcloud builds submit --tag <artifact-url>
| Deploy job	                  | gcloud run jobs create athlete-job --image <artifact-url>
| Run job	                      | gcloud run jobs execute athlete-job
| Update job after code changes	| Rebuild → gcloud run jobs update
| Check logs	                  | gcloud run jobs executions list / describe
