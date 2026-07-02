# Athlete-Dashboard

An automated, modern data stack (MDS) data engineering platform designed to orchestrate the Extract-Load (EL) ingestion of personal fitness metrics from the Strava API into Google BigQuery, execute transformation pipelines via dbt Core, and visualize biometric analytics through an interactive Streamlit application. All infrastructure is declaratively managed via Terraform.

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![GCP App](https://img.shields.io/badge/GCP-Cloud--Run-orange.svg)](https://cloud.google.com/run)
[![Terraform as IAC](https://img.shields.io/badge/IAC-Terraform-mediumpurple.svg)](https://developer.hashicorp.com/terraform)
[![dbt Version](https://img.shields.io/badge/dbt--core-1.11.2-orange.svg)](https://www.getdbt.com/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-Ready-brightgreen.svg)](src/dashboard/Home.py)
[![CI/CD Pipelines](https://img.shields.io/badge/CI-Ruff%20%7C%20Mypy%20%7C%20Bandit-FF4B4B.svg)](https://github.com/XaverHeuser/athlete-dashboard/actions)

---

## 🚀 Key Features

- **Automated EL Pipelines**: Containerized python workers script sync routines pulling activities, athletic gear profiles and precise time-series GPS coordinate activity streams natively from the Strava REST API
- **Infrastructure as Code (IaC)**: Comprehensive Terraform blueprints managing the lifecycle of all Google Cloud Platform components, including BigQuery datasets, Secret Manager resources, Cloud Run Jobs, Artifact Registry repositories, and strict least-privilege IAM bindings
- **Dimensional Data Modeling (dbt)**: Transforms unstructured raw relational database fields into an analytical Star Schema, materializing standardized tables (Fact and Dimension tracking) optimized for analytical aggregation
- **Multi-Sport Consistency Analytics**: Programmatically structures sophisticated mathematical metrics like multi-sport weekly consistency and localized training readiness indices inside intermediate SQL view mappings
- **Interactive Multi-Page Streamlit App**: A high-performance tracking portal providing athletes with dynamic geographic data charts, workout calendars, performance profiles and localized machine-learning readiness forecasts powered by Gemini/Vertex AI
- **Cloud-Native CI/CD Orchestration**: Built with independent validation workflows (`ci-pipeline.yml`, `deploy.yml`) and isolated Cloud Run environment recipes to decouple ingestion workers from presentation layers

---

## 🏗 System Architecture

The diagram below illustrates how components interact across your environment boundaries—from Strava OAuth handshakes to Google Cloud Platform data storage, dbt modeling layers, and Streamlit visualization:

[![Architecture](https://img.plantuml.biz/plantuml/svg/ZLN1Rjim3BthAxZqqXs2tNCOcZP1a245ihRRC610mTYCBKIM34bkcWtzzr6I7RjPKoo7GABU8vyeahvo7grlAWLJNohoz3X3LsuCslnngRSMdRTDvXjBueClgIAe5Kejt4xg6YrMa9cgDfgql_S7HM0fywWBHK9Wves5qJT7TWJe82n4faoJmsZ-xCbgvB3h9SnrNXkflHl17m7yE_g4qRst-8G15dsaRI1Th6HH-hNKE_4Yn83nGDRYrjWg4euxkBYbN3RLkh5rKDSAMHZ3Ok4cxjOAVSHUBcxM7oEV5_-AIkZxhAIyKUtjZhjMsRLgAFBYNutP3Wk2qTHwkUNCm1qLafDxY6IsyhuDT19ile9b5RYNCvFjo2PTqSH7ATXFKihitsBd6t-MFkEpV_WlRuXEzxrhD7mn6nSTH5Em90SBIwJFoMTIvCnNlFelnHs3rsSffsfpzBX1HyStlPR5ruRiuPU-dF4P_41BfMaSfHHqnwttcmFgmGDiZShvBKSk5joZnNqatU5-XGUkupCuRgT2wgAjrRX-3mzSzMGhBapqb1vcO7YNMN7VfgUu3QiUEqZ98AlVoNfwXkaIFi62Agbbv2OpMo_QldZTIznkX9MI7gPrtJLWQnayl12Xjs4y_jnMyWJMZIl9GQgvL6wkHnszJDA5kI4SxAKlWI-NyMmfe3RMenAY3nY8dTv9k4buSK2U8WSdtGcmJye4LWPpbz3StV0aNODA_aOlZNP2z2CY4BdXMRqrZEBZeEHa3gOg7Yl6jatOHOXRqTPi3-0sUuqG_QmOvuoA7YVmO6LHa0rzmjF4ojgBBbXAMPfy4uZLp1Cqf8qr3a1TURQO49HlC00aSODOeTiUB6eN4j1cfBi1uxicQHs-HWfnHJhdZyTV)](https://editor.plantuml.com/uml/ZLN1Rjim3BthAxZqqXs2tNCOcZP1a245ihRRC610mTYCBKIM34bkcWtzzr6I7RjPKoo7GABU8vyeahvo7grlAWLJNohoz3X3LsuCslnngRSMdRTDvXjBueClgIAe5Kejt4xg6YrMa9cgDfgql_S7HM0fywWBHK9Wves5qJT7TWJe82n4faoJmsZ-xCbgvB3h9SnrNXkflHl17m7yE_g4qRst-8G15dsaRI1Th6HH-hNKE_4Yn83nGDRYrjWg4euxkBYbN3RLkh5rKDSAMHZ3Ok4cxjOAVSHUBcxM7oEV5_-AIkZxhAIyKUtjZhjMsRLgAFBYNutP3Wk2qTHwkUNCm1qLafDxY6IsyhuDT19ile9b5RYNCvFjo2PTqSH7ATXFKihitsBd6t-MFkEpV_WlRuXEzxrhD7mn6nSTH5Em90SBIwJFoMTIvCnNlFelnHs3rsSffsfpzBX1HyStlPR5ruRiuPU-dF4P_41BfMaSfHHqnwttcmFgmGDiZShvBKSk5joZnNqatU5-XGUkupCuRgT2wgAjrRX-3mzSzMGhBapqb1vcO7YNMN7VfgUu3QiUEqZ98AlVoNfwXkaIFi62Agbbv2OpMo_QldZTIznkX9MI7gPrtJLWQnayl12Xjs4y_jnMyWJMZIl9GQgvL6wkHnszJDA5kI4SxAKlWI-NyMmfe3RMenAY3nY8dTv9k4buSK2U8WSdtGcmJye4LWPpbz3StV0aNODA_aOlZNP2z2CY4BdXMRqrZEBZeEHa3gOg7Yl6jatOHOXRqTPi3-0sUuqG_QmOvuoA7YVmO6LHa0rzmjF4ojgBBbXAMPfy4uZLp1Cqf8qr3a1TURQO49HlC00aSODOeTiUB6eN4j1cfBi1uxicQHs-HWfnHJhdZyTV)

---

## ⚙️ Configuration & Environment Setup

The ingestion pipelines and Streamlit components load target warehouse contexts using environment variables. Initialize these keys within your running workspace environment:

Variable Name |	Description | Example Target Context
--------- | --------------- | --------------
GCP_PROJECT_ID	| Targeted Google Cloud Platform Project ID | project-id
BIGQUERY_DATASET | Target dataset ID configured inside your BigQuery data warehouse | strava_analytics
STRAVA_CLIENT_ID | Application identifier generated by the Strava API management portal | 123456
STRAVA_CLIENT_SECRET | Cryptographic secret key used to handle OAuth token refreshes | a1b2c3d4e5f6g7h8...
STRAVA_REFRESH_TOKEN | Persistent token used to fetch short-lived active request bearers | 9876543210abcdef...

---

## 🛠 Cloud Infrastructure Provisioning (Terraform)

This platform provides full infrastructure definition scripts inside the /terraform folder. The resources are decoupled structurally by architectural concern.

### 1. Prerequisites

- Terraform CLI installed locally.
- Google Cloud SDK (gcloud) authenticated against your target platform account

### 2. Initialization and Deployment

Navigate to the terraform directory and initialize the cloud backend provider layers:

```bash
cd terraform

# Initialize the workspace and download necessary Google provider modules
terraform init

# Audit resource change specifications before modifying existing states
terraform plan

# Execute provisioning blueprints 
terraform apply
```

### 3. Populate Application Secrets

Go to the Secret Manger in GCP and update each secret with a new  version of your own strava secrets.

---

## 💻 Local Workspace Installation

### 1. Project Initialization

```bash
# Clone the repository structure locally
git clone [https://github.com/XaverHeuser/athlete-dashboard.git](https://github.com/XaverHeuser/athlete-dashboard.git)
cd athlete-dashboard

# Setup an isolated Python virtual runtime environment
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Dependency Management Execution

This repository isolates dependencies based on the current execution context. Run the following setup blocks based on your needs:

```bash
# Upgrade core package management tools to identical base lines
python -m pip install --upgrade pip==26.1.1

# Option A: Install Streamlit presentation layer and ingestion pipeline layers
python -m pip install -r requirements.txt

# Option B: Install dbt Core framework and BigQuery database adapters
python -m pip install -r requirements-dbt.txt

# Option C: Deploy quality verification layers (linters, type-checkers, unit tests)
python -m pip install -r requirements-dev.txt
```

### 3. Initialize Local dbt Profiles

To execute your models locally against BigQuery, set up a standard profiles.yml file pointing to your Google Cloud credentials file:

```yaml
# ~/.dbt/profiles.yml
athlete_dashboard:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: service-account
      project: your-gcp-project-id
      dataset: strava
      threads: 4
      keyfile: /path/to/your/gcp-service-account-key.json
      timeout_seconds: 300
      priority: interactive
      retries: 1
```

Verify your database connections and launch compilation tasks using the commands below:

```bash
cd dbt
dbt deps     # Fetch external dependency libraries (dbt_utils)
dbt debug    # Validate infrastructure connectivity parameters
dbt run      # Execute downstream database transformations
dbt test     # Run schema data integrity test invariants
```

### 4. Running the Dashboard Application Locally

Launch the application shell to host the Streamlit analytical platform on a local network server:

```bash
streamlit run src/dashboard/Home.py
```

---

## ☁️ Continuous Integration & Deployment (CI/CD)

### Automated Pull Request Safeguards

The configured repository uses a unified GitHub Actions pipeline (`ci-pipeline.yml`) to enforce code standards on every merge request into the main branch:

- **Quality Checks:** Audits syntax and formatting rules using Ruff.
- **Static Type Checking:** Evaluates explicit type annotations using strict mypy configurations.
- **Security Auditing:** Scans files for exposed credentials or vulnerabilities using Bandit.

### Automated Build and Push

A GitHub Action pipeline (`deploy.yml`) will be executed on every push to the main branch. It builds and pushed the el and dbt Docker Images to GCPs Artifacts Registry. Both Cloud Run Jobs (el & dbt job) will be updated with the new created image.

### Google Cloud Build Automated Pipelines

The data platform splits build automation into specialized pipelines to reduce runtime overhead:

- **EL Ingestion Pipeline (cloudbuild.el.yaml):** Automatically builds the ingestion image, pushes the updated artifact layer, and deploys it to target container environments.
- **dbt Transformation Pipeline (cloudbuild.dbt.yaml):** Packages dbt execution entry points into an isolated environment to run modeling tasks on a scheduled trigger.

---

## 📂 Repository Structure

```text
├── .github/                 # Automated validation workflows & dependency maintenance engines
│   └── workflows/
│       └── ci-pipeline.yml  # Comprehensive Continuous Integration pipeline definitions
|       └── deploy.yml       # Automated Deployment
├── dbt/                     # dbt Core modern data stack transformation definitions
│   ├── macros/              # Custom modular SQL script injections (discipline mappings)
│   ├── models/              # Multi-tier SQL transformation layers
│   │   ├── intermediate/    # Aggregations, consistency scripts, logic layer splits
│   │   ├── marts/           # Production Star Schema models (Fact & Dim tracking)
│   │   └── staging/         # Initial field renaming and casting layers
│   ├── dbt_project.yml      # Core dbt project properties metadata manifest
│   └── profiles.yml         # BigQuery cloud database driver connection profiles
├── notebooks/               # Local diagnostic exploratory environments and integration sandboxes
├── src/                     # Core codebase modules
│   ├── dashboard/           # Multi-page interactive Streamlit presentation layer app
│   │   └── pages/           # Targeted analytics pages (AI, Gear, Profile, Calendar)
│   ├── ingestion/           # Data platform extraction and ingestion pipelines
│   └── models/              # Pydantic data modeling structural schema rules
├── terraform/               # Infrastructure as Code (IaC) configuration blueprints
│   ├── bigquery.tf          # Declarative BigQuery multi-layer datasets (raw, staging, mart)
│   ├── cloudbuild.tf        # Cloud Storage bucket configurations and deployment triggers
│   ├── el_pipeline.tf       # Extract-Load job constructs and Secret environment injections
│   ├── ...
├── Dockerfile               # Production container definition for Streamlit app
├── Dockerfile.dbt           # Production container configuration for dbt run workers
├── cloudbuild.dbt.yaml      # GCP build pipeline automation for dbt transform workflows
├── cloudbuild.el.yaml       # GCP build pipeline automation for extract-load workflows
└── pyproject.toml           # Unified configuration file for linters, type checkers, and tool definitions
```

---

##  Strava Developer API Changes

Strava changed the developer API. Only members with a subscription can access the API.
Due to this, no new data will be loaded. The Cloud scheduler trigger is paused.

```
Effective June 30, 2026

Subscription required for existing Standard Tier developers.
A Strava subscription will be required to access the API as a Standard Tier developer.
Extended Access Tier developers are not affected.
```

---

## 📄 License

Distributed directly under the terms of the open-source MIT License guidelines. See the standard accompanying LICENSE text metadata file for deep details.
