# Athlete Dashboard – Architecture (ELT)

*Last updated: 2025-10-28*

## 0) Executive Summary

This project follows a modern **ELT** pattern on Google Cloud: a scheduled Cloud Run job **extracts** activities from Strava and **loads** raw JSON into BigQuery (`raw`), and **transforms** data inside BigQuery with SQL/dbt into `staging` and `marts`. A Streamlit app (planned) will query the `mart` layer for fast, simple visualizations.

## 1) Current Status

* Repository scaffolding present: Dockerfiles for app and dbt, Cloud Build config, dbt project folder, `src` for Python jobs, `notebooks` for exploration.
* Implementation status (as of this document):

  * **Extract/Load**: In progress (incremental Strava fetch planned).
  * **Transform (dbt/BigQuery)**: In progress; dbt project initialized, models in progress.
  * **Presentation (Streamlit)**: In progress.

## 2) High-Level Architecture

```
+------------------+        +---------------------+        +------------------------------+
| Google Cloud     |        | Cloud Run:          |        | BigQuery                     |
| Scheduler        +------->+ "extract-load" job  +------->+ raw.strava_activities        |
| (cron)           |        | (Python, Docker)    |        |  (Bronze)                    |
+------------------+        +---------------------+        +---------------+--------------+
                                                                     | (dbt transforms)
                                                                     v
                                                          +----------+-----------+
                                                          | BigQuery (staging)   |
                                                          | cleaned/normalized  |
                                                          +----------+-----------+
                                                                     | (dbt)
                                                                     v
                                                          +----------+-----------+
                                                          | BigQuery (mart)     |
                                                          | aggregates/marts    |
                                                          +----------+-----------+
                                                                     |
                                                                     v
                                                          +----------+-----------+
                                                          | Streamlit Dashboard |
                                                          | (query mart tables) |
                                                          +---------------------+
```

## 3) Components

### 3.1 Cloud Scheduler

* Triggers the Cloud Run **extract-load** service on an daily basis.
* Cron examples: `0 7 * * *` CET.

### 3.2 Cloud Run (Extract & Load)

* Container built from `Dockerfile`.
* Entrypoint Python script (in `src/`) performs:

  1. **Auth** with Strava via OAuth2 refresh token (stored in Secret Manager).
  2. **Incremental pull**: request new/updated activities since the last successful watermark (persisted in `raw._ingestion_state` or in Secret Manager/Parameter Store).
  3. **Load** Dataframes from JSON payloads into BigQuery table `raw.strava_activities` (schema: pass-through of Strava fields + metadata columns like `ingested_at`, `source`, `activity_id`).
  4. **Idempotency**: upsert by `activity_id`; deduplicate on repeated fetches.
  5. **Observability**: structured logs to Cloud Logging; non-200 responses retried with backoff.

### 3.3 BigQuery Datasets

* **`raw` (Bronze)**: immutable(ish) event-level JSON from Strava; minimal shaping only.
* **`staging`**: cleaned, typed tables; examples:

  * `staging.activities` (typed fields, units normalized, coordinates geo-typed where appropriate)
* **`marts`**: denormalized marts & aggregates optimized for the dashboard; examples:

  * TBD.

### 3.4 Transformations with dbt (or Dataform)

* Separate container (`Dockerfile.dbt`) to run dbt against BigQuery.
* **Model flow**: `raw` → `staging` (staging + type casting) → `mart` (aggregates/marts).
* **Scheduling**: run dbt after each successful load (Cloud Scheduler chain, Cloud Build, or a single Orchestrator job that runs EL then T).
* **Tests**: dbt tests for uniqueness (`activity_id`), non-null constraints, referential integrity across child tables.

### 3.5 Streamlit Frontend (Planned)

* Queries `mart` tables only for performance and simplicity.
* Example pages:

  * **Overview**: mileage/time/elevation by period; activity mix.
  * **Trends**: rolling 7/28/90-day charts; YoY comparisons.
  * **Records**: fastest 5k/10k, longest ride/run, peak power/HR (if available).
  * **Map**: route visualizations (if polyline/coords available in `staging`).

## 4) Data Contracts & Schemas

TBD.

## 5) Orchestration & Scheduling

Two common setups:

1. **Split jobs**: Scheduler → Run EL container → (on success) Scheduler/Trigger → Run dbt container.
2. **Unified job**: one Cloud Run entrypoint that performs EL, then invokes dbt (`dbt deps && dbt run && dbt test`).

Watermarking:

* Store `last_successful_start_date` (epoch seconds) for Strava `/athlete/activities?after=...` and update on success.

Retries/alerts:

* HTTP retries (exponential backoff), transient error retries for BigQuery load jobs.
* Optional: alerting via Cloud Monitoring policy on Cloud Run 5xx or job failures.

## 6) Security & Secrets

* **Strava OAuth**: store client_id, client_secret, refresh_token in **Secret Manager**; refresh access token at runtime.
* **GCP Auth**: service account with least privilege; roles: `BigQuery Data Editor` on project/datasets; `Secret Manager Secret Accessor`.
* **Network**: public egress allowed; optionally VPC connector if needed.
* **PII**: athlete name/email not stored unless required; prefer athlete numeric ID.

## 7) DevEx & CI/CD

* **Cloud Build** builds containers from `Dockerfile` and `Dockerfile.dbt` and can deploy to Cloud Run.
* **Formatting/Linting**: ruff, mypy configured in repo.
* **Local dev**: `.env` + `streamlit secrets` for BigQuery billing project and credentials; run EL locally with a service account key (do not commit).
* **dbt**: `profiles.yml` (BigQuery target) stored via environment variables/Secret Manager; run `dbt run` and `dbt test` locally against a sandbox dataset.

## 8) Observability

* **Cloud Logging**: structured logs with request IDs and activity IDs.
* **BigQuery**: job history + INFORMATION_SCHEMA for lineage/latency metrics.
* **dbt docs**: optional `dbt docs generate` and host via Cloud Run static container.

## 9) Open Questions / TODO

* Define final `staging/*` and `mart/*` models and acceptance criteria (SLAs for freshness, query times).
* Decide on Strava **streams** ingestion (route points, HR/power streams) and table design.
* Evaluate Strava **webhooks** for near‑real‑time updates vs. polling.
* Add first Streamlit MVP page wired to `mart.activity_summary_*`.
* Add integration tests (fixture activities → expected aggregates).

## 10) Appendix

**Why ELT over ETL?**

* Pushes heavy transforms into BigQuery for elasticity, cost visibility, and reprocessing on demand while keeping raw data intact.

**Naming conventions**

* Datasets: `raw`, `staging`, `mart`.
* Tables: snake_case; staged models prefixed with `stg_` in dbt.

**Timezones**

* Store timestamps in UTC; surface Europe/Berlin (user’s TZ) in the dashboard.
