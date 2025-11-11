# dbt Profiles & Connections

The **`profiles.yml`** file defines how dbt connects to your data warehouse.  
It contains connection credentials, environment targets (like `dev` or `prod`), and performance settings (e.g., threads, timeouts).  

In this project, we use **BigQuery** as our data warehouse.

---

## Overview

dbt reads configuration from a file named **`profiles.yml`**, typically located at: `~/.dbt/profiles.yml`

Each dbt project references one **profile name** that defines:

- The **warehouse type** (e.g., BigQuery, Snowflake, Postgres)
- One or more **environments** (`dev`, `prod`, etc.)
- Credentials and project/dataset info
- Runtime options (threads, timeout)

> You can check your active profile in `dbt_project.yml` under the `profile:` key.

---

## Example: BigQuery Profile

```yaml
strava_project:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: oauth
      project: athlete-dashboard-467718
      dataset: strava_data_dev
      threads: 4
      timeout_seconds: 300

    prod:
      type: bigquery
      method: service-account
      keyfile: /secrets/service_account.json
      project: athlete-dashboard-467718
      dataset: strava_data
      threads: 8
      timeout_seconds: 600
```

### Key Points

- target: the default environment dbt uses (dev here).
- outputs: defines connection details per environment.
- method:
  - oauth → uses your Google account authentication (good for local dev).
  - service-account → uses a JSON key file (for CI/CD or production).

---

## BigQuery Profile Parameters

| Parameter         | Description                                               | Example                    |
| ----------------- | --------------------------------------------------------- | -------------------------- |
| `type`            | Must be `bigquery` for BigQuery projects.                 | `bigquery`                 |
| `method`          | Authentication method (`oauth` or `service-account`).     | `oauth`                    |
| `project`         | GCP project ID.                                           | `athlete-dashboard-467718` |
| `dataset`         | Default dataset/schema for dbt models.                    | `strava_data`              |
| `threads`         | Number of concurrent queries dbt runs.                    | `4`                        |
| `timeout_seconds` | Max time dbt waits for a query.                           | `300`                      |
| `keyfile`         | Path to service account key (if using `service-account`). | `/path/to/key.json`        |
| `priority`        | Query priority (`interactive` or `batch`).                | `interactive`              |

---

## Authentication Options

1️⃣ OAuth (Local Development)

Simplest method — dbt uses your logged-in Google credentials.

Run gcloud auth application-default login

Set method: oauth in profiles.yml

Ideal for personal or dev environments

2️⃣ Service Account (CI/CD or Production)

Use a service account with restricted permissions.

Download the service account key JSON

Store it securely (e.g., /secrets/service_account.json)

Reference it in profiles.yml:

```yaml
method: service-account
keyfile: /secrets/service_account.json
```

Never commit this file to Git — use secrets management.

---

## Environment Setup

Define multiple **targets** for different environments.

```yaml
strava_project:
  target: dev
  outputs:
    dev:
      dataset: strava_data_dev
    staging:
      dataset: strava_data_stg
    prod:
      dataset: strava_data_prod
```

Switch environments with:

```bash
dbt run --target prod
```

This allows you to:

Develop in isolation

Test transformations in staging

Deploy to production confidently

---

## Best Practices

| Area                 | Recommendation                                                               |
| -------------------- | ---------------------------------------------------------------------------- |
| **Credentials**      | Store secrets outside Git (CI/CD vaults, env vars, key stores).              |
| **Environments**     | Separate datasets per environment (`_dev`, `_stg`, `_prod`).                 |
| **Threading**        | Use 4–8 threads for parallel model execution.                                |
| **Timeouts**         | Increase for heavy marts or reports (up to 600s).                            |
| **Profile Naming**   | Match the profile name with the dbt project name.                            |
| **IAM Roles**        | Use least-privilege service accounts (read raw data, write marts).           |
| **Regional Configs** | Ensure dataset regions match project settings.                               |
| **Profiles in CI**   | Load `profiles.yml` from environment or secret store, not checked into repo. |

---

## Secrets Management

Use environment variables for secure authentication in CI/CD.

Example using GitHub Actions:

```yaml
env:
  GOOGLE_APPLICATION_CREDENTIALS: ${{ secrets.GCP_KEY }}
```

Then in `profiles.yml`:

```yaml
method: service-account
keyfile: '{{ env_var('GOOGLE_APPLICATION_CREDENTIALS') }}'
```

---

## CI/CD Example (GitHub Actions)

```yaml
# .github/workflows/dbt.yml
name: dbt Build

on: [push, pull_request]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dbt
        run: pip install dbt-bigquery

      - name: Configure BigQuery credentials
        run: echo '$GCP_KEY' > /tmp/keyfile.json
        env:
          GCP_KEY: ${{ secrets.GCP_SERVICE_ACCOUNT_JSON }}

      - name: Run dbt build
        run: dbt build --target prod
        env:
          DBT_PROFILES_DIR: ./ci/
```

Where `ci/profiles.yml` contains:

```yaml
strava_project:
  target: prod
  outputs:
    prod:
      type: bigquery
      method: service-account
      keyfile: /tmp/keyfile.json
      project: athlete-dashboard-467718
      dataset: strava_data_prod
```

---

## Troubleshooting

| Problem             | Cause                                   | Fix                                                                |
| ------------------- | --------------------------------------- | ------------------------------------------------------------------ |
| `No profile found`  | dbt can’t locate `profiles.yml`.        | Ensure file is at `~/.dbt/profiles.yml` or set `DBT_PROFILES_DIR`. |
| `Permission denied` | Insufficient IAM roles.                 | Add BigQuery Data Editor and Job User roles.                       |
| `Invalid keyfile`   | Corrupt or misconfigured JSON key.      | Re-download from GCP IAM → Service Accounts.                       |
| `Timeout exceeded`  | Heavy queries or low timeout.           | Increase `timeout_seconds`.                                        |
| `Profile mismatch`  | Project name doesn’t match profile key. | Update `profile:` in `dbt_project.yml`.                            |

---

## Example Local Setup Workflow

### Authenticate to GCP

```bash
gcloud auth application-default login
```

### Verify credentials

```bash
gcloud auth list
```

### Create or edit your profile

```bash
code ~/.dbt/profiles.yml
```

### Run dbt commands

```bash
dbt debug
dbt run
```

---

## Example Folder Structure

```bash
~/.dbt/
│
├── profiles.yml         # Local connection settings
└── logs/                # dbt logs
```

In your repo:

```bash
/docs/
  ├── dbt_profiles.md
  ├── dbt_overview.md
  ├── dbt_testing.md
  └── ...
```

---

## Security Checklist

- Never commit credentials or key files
- Use separate service accounts per environment
- Restrict service accounts to minimal IAM roles
- Rotate keys periodically
- Encrypt secrets in CI/CD
- Log dbt job runs (audit trail)
- Use dbt debug to validate connection before runs

---

## Final Notes

- The profiles.yml file defines how and where dbt runs — treat it like your connection blueprint.
- Keep environments isolated, credentials secure, and datasets clearly named.
- Use automation for deployment, not manual credentials.

> “A clean dbt profile keeps your pipelines safe, fast, and predictable.”
