# GCP Setup Notes

1. Terminal
PROJECT=dein-gcp-projekt-id
gcloud config set project $PROJECT

gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  cloudscheduler.googleapis.com \
  secretmanager.googleapis.com \
  iam.googleapis.com \
  pubsub.googleapis.com

2. Cloud Run Service

3. Dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Quellcode kopieren
COPY . .

# Default command: passe main.py an deinen Einstiegspunkt an
CMD ["python", "src/main.py"]

4. Execute commands
docker build -t myscript:local .
docker run --rm myscript:local

5. 



6. 



7. 

