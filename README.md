# Athlete-Dashboard

> Personal, extensible, and self-hosted dashboard for athletic activities powered by a modern ELT stack on Google Cloud.

---

## Project Goal & Motivation

Create a personal data platform for your training history. Pull activities from Strava (and later Garmin), load raw JSON into BigQuery, and transform it with dbt into fast, analytics-ready tables that a Streamlit dashboard can query.

---

## Project Status

> **Status**: *In Development* - Architecture and scaffolding exist; core components are being implemented.

- Containers: Dockerfile (EL job) and Dockerfile.dbt (dbt runner)
- Infra scaffolding: cloudbuild.yaml
- dbt project: dbt/
- Python src for ingestion: src/
- Exploration: notebooks/

---

## Key Features

- Automated Data Sync (Cloud Scheduler → Cloud Run)
- Historical Archive (BigQuery raw/staging/marts)
- Interactive Dashboard (Streamlit)
- Custom Analytics (TSS/TRIMP-like, PRs, YoY trends) *(Planned)*
- Multi‑Source Ready *(Strava now; Garmin next)*



## Technology Stack

| Component      | Technology               | Description                             |
| -------------- | ------------------------ | --------------------------------------- |
| Data Source    | Strava API               | Source of raw activity data             |
| Cloud          | Google Cloud Platform    | Hosting for Run, Scheduler, BQ, Secrets |
| Data Warehouse | BigQuery                 | Bronze → staging → marts datasets         |
| EL             | Python 3.9+ on Cloud Run | Extract & Load raw JSON into `raw`      |
| T              | dbt (BigQuery)           | SQL transforms to `staging`/`marts`       |
| Scheduling     | Cloud Scheduler          | Triggers EL job (this triggers dbt-job)    |
| Frontend       | Streamlit                | Queries `marts` for fast UX              |

---

## Project Structure

```bash
Athlete-Dashboard/
├─ .github/                     # CI configs (future)
├─ dbt/                         # dbt project (models, seeds, tests, macros)
├─ docs/                        # Documentation (architecture, how‑tos)
├─ notebooks/                   # Jupyter exploration
├─ src/                         # Python EL job (Strava → BigQuery)
├─ Dockerfile                   # EL container
├─ Dockerfile.dbt               # dbt runner container
├─ cloudbuild.yaml              # Build/deploy pipelines
├─ requirements*.txt            # Python deps (core/dev/dbt)
└─ README.md
```

---

## Workflow (ELT)

### 1. Extract & Load (Cloud Run)

- Refresh Strava OAuth token (Secret Manager), fetch **incremental** activities since the last watermark.
- Load raw payloads into BigQuery `raw.strava_activities` with metadata (`ingested_at`, `activity_id`, `source`).
- Idempotent upsert by `activity_id` (dedupe).

### 2. Transform (dbt on BigQuery)

- `raw → staging`: type casting, unit normalization, cleanup.
- `staging → marts`: aggregates (daily/monthly summaries, PRs, training load).
- dbt tests: uniqueness, not-null, references.

### 3. Present (Streamlit)

- Pages: Overview, Trends, Records, Maps.
- Read-only queries against `marts` only.

See [Architecture Docs](./docs/architecture/architecture.md) for more info.

---

## Getting Started (Local Dev)

TBD.

---

## Deploying on GCP (Sketch)

> See [GCP Deployment docs](./docs/gcp/deployment.md)

---

## Roadmap

- Phase 1: ELT core (Strava → BQ raw/staging/marts; dbt models/tests)
- Phase 2: Streamlit MVP (overview + filters)
- Phase 3: Garmin + advanced metrics (TSS/Fitness/Fatigue), optional Postgres path

---

## License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.
