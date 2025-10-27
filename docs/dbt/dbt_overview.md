# dbt (Data Build Tool) — Overview

dbt lets you **transform, test, and document data** directly inside your data warehouse — without needing a separate ETL tool.  
It turns SQL into a fully version-controlled transformation framework with **testing, documentation, and lineage tracking** built in.

---

## What Is dbt?

**dbt (data build tool)** helps data teams:

- Transform raw data already loaded into your warehouse (e.g., BigQuery)
- Build modular SQL models that depend on each other
- Test and validate data quality
- Generate documentation automatically
- Integrate with Git and CI/CD for automated builds

Think of dbt as the **“T” in ELT** — it focuses only on the **Transform** step.

---

## Core Concepts

| Concept | Description | Example |
|----------|--------------|----------|
| **Model** | A SQL file that defines a transformation. | `models/staging/stg_orders.sql` |
| **Source** | A definition of where raw data lives. | `raw.orders` |
| **ref()** | Declares dependencies between models. | `select * from {{ ref('stg_orders') }}` |
| **schema.yml** | Describes models, columns, and tests. | `models/staging/schema.yml` |
| **Snapshot** | Tracks historical changes in source data. | `snapshots/athletes_snapshot.sql` |
| **Seed** | CSV files versioned with your code. | `data/countries.csv` |
| **Macro** | Jinja functions for reusable SQL logic. | `{{ clean_string('email') }}` |
| **Test** | Data quality check (built-in or custom). | `not_null`, `unique`, `accepted_values` |

---

## Typical Project Layout

A dbt project is structured in clear layers:

```yaml
dbt_project/
├── models/
│ ├── staging/
│ │ ├── stg_orders.sql
│ │ ├── stg_customers.sql
│ │ └── schema.yml
│ ├── marts/
│ │ ├── fct_orders.sql
│ │ ├── dim_customers.sql
│ │ └── rpt_revenue_daily.sql
│ └── schema.yml
├── snapshots/
│ └── athletes_snapshot.sql
├── tests/
│ └── test_positive_distance.sql
├── macros/
│ └── clean_string.sql
└── dbt_project.yml
```

Each folder represents a **layer** in the transformation process:

- `staging/`: cleaning and standardizing raw source data  
- `marts/`: business logic — facts, dimensions, reports  
- `snapshots/`: historical state tracking  
- `tests/`: reusable validation queries  
- `macros/`: helper logic

---

## Typical dbt Workflow

### Build Models

```bash
dbt run
```

Builds or updates all SQL models.
Use `--select` to limit which ones to build:

```bash
dbt run --select stg_activities
```

### Test Data Quality

```bash
dbt test
```

Runs all tests defined in schema.yml.
See [dbt Testing](./dbt_testing.md) for details.

### Generate Documentation

```bash
dbt docs generate
dbt docs serve
```

Launches a local data catalog (default: http://localhost:8080) with:

- Model descriptions
- Lineage graph
- Column-level metadata
- Test results

### Run Snapshots

```bash
run snapshot
```

Captures changes in mutable data over time.
See [dbt Snapshots](./dbt_snapshots.md) for setup details.

---

## Command Reference

| Command                | Description                                    |
| ---------------------- | ---------------------------------------------- |
| `dbt run`              | Builds models.                                 |
| `dbt test`             | Executes all tests.                            |
| `dbt build`            | Runs models, tests, and snapshots in sequence. |
| `dbt docs generate`    | Generates documentation site.                  |
| `dbt docs serve`       | Serves docs locally.                           |
| `dbt snapshot`         | Captures historical changes.                   |
| `dbt source freshness` | Checks if source data is current.              |
| `dbt run --select`     | Run specific models only.                      |

---

## Example Data Flow

raw.orders ──> stg_orders ──> fct_orders ──> rpt_orders_daily

| Layer          | Prefix | Purpose                            | Granularity           |
| -------------- | ------ | ---------------------------------- | --------------------- |
| **Staging**    | `stg_` | Clean, standardize raw data        | 1 row = source record |
| **Facts**      | `fct_` | Transactional data                 | 1 row = order         |
| **Dimensions** | `dim_` | Entities (customer, product, etc.) | 1 row = entity        |
| **Reports**    | `rpt_` | Aggregated summaries for BI        | 1 row = time period   |

For naming conventions, see [dbt Guidelines](./dbt_guidelines.md)

---

## Best Practices

| Category            | Recommendation                                         |
| ------------------- | ------------------------------------------------------ |
| **Granularity**     | Always define “1 row = X”.                             |
| **Model Purpose**   | One model per logical transformation.                  |
| **Naming**          | Prefix with `stg_`, `fct_`, `dim_`, or `rpt_`.         |
| **Dependencies**    | Always use `ref()` instead of hardcoding table names.  |
| **Testing**         | Add `not_null` and `unique` tests for every key field. |
| **Materialization** | Use **views** for staging, **tables** for marts.       |
| **Docs**            | Keep schema.yml updated — it’s your data catalog.      |
| **Version Control** | Commit SQL + YAML + seeds to Git.                      |
| **CI/CD**           | Automate `dbt build` in your pipeline.                 |

---

## BigQuery Integration

Example `profiles.yml` setup:

```yaml
strava_project:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: oauth
      project: athlete-dashboard-467718
      dataset: strava_data
      threads: 4
      timeout_seconds: 300
```

See [dbt Profiles](./dbt_profiles.md) for details on authentication, service accounts and environments.

---

## Where to Go Next

| Topic                                 | Description                                |
| ------------------------------------- | ------------------------------------------ |
| [dbt Guidelines](./dbt_guidelines.md) | Core modeling rules and naming conventions |
| [dbt Staging](./dbt_staging.md)       | How to build clean staging models          |
| [dbt Marts](./dbt_marts.md)           | Facts, dimensions, and reporting models    |
| [dbt Testing](./dbt_testing.md)       | Schema.yml structure and data tests        |
| [dbt Snapshots](./dbt_snapshots.md)   | Capturing historical changes               |
| [dbt Profiles](./dbt_profiles.md)     | Connecting dbt to BigQuery                 |

---

## References

- [dbt Official Documentation](https://docs.getdbt.com/)
- [dbt Learn (Free Courses)](https://learn.getdbt.com/catalog)
- [dbt Community Slack](https://www.getdbt.com/community)
- [dbt Labs GitHub](https://github.com/dbt-labs)

---

## Final Notes

- dbt is code-first: every transformation, test, and schema is versioned in Git.
- Tests are just SQL — if a query returns rows, the test fails.
- Documentation isn’t optional — it’s part of your model definition.
- Keep your transformations simple, modular, and testable.

> “In dbt, you don’t move data — you make it meaningful.”
