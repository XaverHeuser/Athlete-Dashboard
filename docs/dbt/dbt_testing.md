# dbt Testing & Data Quality

Data quality is the backbone of every trustworthy analytics system.  
In dbt, **tests** validate assumptions about your data — automatically, continuously and close to your SQL logic.

This document explains how dbt tests work, how to define them in `schema.yml`, how to create custom tests and how to integrate testing into your workflows.

---

## Purpose

dbt tests ensure that your data:

- Matches expected structure and rules  
- Contains valid and unique keys  
- Maintains referential integrity across models  
- Contains only allowed or expected values  
- Doesn’t break when source data changes  

> **Goal:** Catch bad data before it reaches BI dashboards.

---

## Types of Tests

| Type | Description | Example |
|------|--------------|----------|
| **Generic (Built-in)** | Predefined dbt tests like `unique`, `not_null`, `accepted_values`, etc. | Simple YAML definitions |
| **Custom SQL Tests** | User-defined queries that return failing rows. | `tests/test_positive_distance.sql` |
| **Schema-level Tests** | Defined in `schema.yml` for models, columns, or sources. | Model metadata + tests in YAML |
| **Data Tests (Standalone)** | Independent test files that run arbitrary SQL logic. | Complex multi-table validations |

---

## Defining Tests in `schema.yml`

Every model should have a **`schema.yml`** that defines:

- Model description  
- Column descriptions  
- Data tests  

### Example

```yaml
version: 2

models:
  - name: stg_activities
    description: "Cleans and standardizes Strava activity data."
    columns:
      - name: activity_id
        description: "Unique identifier for each activity."
        tests:
          - not_null
          - unique
      - name: athlete_id
        description: "Foreign key to dim_athletes."
        tests:
          - not_null
          - relationships:
              to: ref('dim_athletes')
              field: athlete_id
      - name: activity_type
        description: "Type of sport or activity (e.g., Run, Ride, Swim)."
        tests:
          - accepted_values:
              values: ['Run', 'Ride', 'Swim']
```

---

## How dbt Tests Work

When you run:

```bash
dbt test
```

dbt:

1. Parses all `schema.yml` and `sources.yml` files
2. Compiles tests into SQL queries
3. Executes them in your warehouse (e.g., BigQuery)
4. Reports pass/fail results

- Pass: The query returns zero rows
- Fail: The query returns one or more rows

Example:

A `not_null` test generates SQL like:

```sql
select *
from {{ ref('stg_activities') }}
where activity_id is null
```

---

## Built-in Tests Reference

| Test                      | Purpose                                         | Example YAML                                                    | Example SQL (simplified)                                                       |
| ------------------------- | ----------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| **`not_null`**            | Ensures a column never contains NULLs.          | `- not_null`                                                    | `select * from table where column is null;`                                    |
| **`unique`**              | Ensures column values are unique.               | `- unique`                                                      | `select column, count(*) from table group by column having count(*) > 1;`      |
| **`accepted_values`**     | Restricts a column to predefined values.        | `- accepted_values: {values: ['Run','Ride']}`                   | `select * from table where column not in ('Run','Ride');`                      |
| **`relationships`**       | Validates foreign key integrity between models. | `- relationships: {to: ref('dim_athletes'), field: athlete_id}` | `select * from child where athlete_id not in (select athlete_id from parent);` |
| **`expression_is_true`**  | Ensures a condition holds for all rows.         | `- expression_is_true: {expression: "distance_m > 0"}`          | `select * from table where not (distance_m > 0);`                              |
| **`not_accepted_values`** | Fails if a column contains disallowed values.   | `- not_accepted_values: {values: ['Error','Unknown']}`          | `select * from table where column in ('Error','Unknown');`                     |

---

## Custom Tests

When built-ins aren’t enough, write your own tests as SQL files under /tests/.

### Example Custom Tests

`tests/test_positive_distance.sql`

```sql
-- Custom test: distance must be non-negative
select *
from {{ ref('stg_activities') }}
where distance_m < 0
```

Run it manually:

```bash
dbt test --select test_positive_distance
```

- Returns no rows → test passes
- Returns rows → test fails and prints failing records

---

## Example: Source Tests

You can also test your raw sources to catch bad upstream data.

```yaml
version: 2

sources:
  - name: strava_raw
    schema: strava_data
    tables:
      - name: activities
        columns:
          - name: id
            tests:
              - not_null
              - unique
          - name: type
            tests:
              - accepted_values:
                  values: ['Run', 'Ride', 'Swim']
```

---

## Data Tests (Advanced)

You can create standalone SQL tests that validate multi-table logic or data patterns.

Example: `tests/test_activity_vs_athlete.sql`

```sql
-- Ensure all activities reference valid athlete_ids
select a.activity_id
from {{ ref('fct_activities') }} a
left join {{ ref('dim_athletes') }} d
  on a.athlete_id = d.athlete_id
where d.athlete_id is null
```

This acts as a cross-model constraint check.

---

## Running Tests

| Command                                    | Description                                                         |
| ------------------------------------------ | ------------------------------------------------------------------- |
| `dbt test`                                 | Run all tests in the project.                                       |
| `dbt test --select stg_activities`         | Run tests for one model.                                            |
| `dbt test --select test_positive_distance` | Run a specific custom test.                                         |
| `dbt build`                                | Runs models + tests together (recommended in CI/CD).                |
| `dbt test --store-failures`                | Store failing rows in a `_dbt_test__failures` table for inspection. |

---

## Testing Strategy by Layer

| Layer                   | Test Focus                                 | Examples                                |
| ----------------------- | ------------------------------------------ | --------------------------------------- |
| **Staging (`stg_`)**    | Data cleanliness and integrity             | `not_null`, `unique`, `accepted_values` |
| **Facts (`fct_`)**      | Referential integrity and metrics validity | `relationships`, `expression_is_true`   |
| **Dimensions (`dim_`)** | Key uniqueness and completeness            | `unique`, `not_null`, `accepted_values` |
| **Reports (`rpt_`)**    | Aggregation sanity checks                  | Custom SQL tests (e.g., totals > 0)     |


---

## CI/CD Integration

Testing should be automated as part of every pull request or pipeline.

### Example CI Workflow

```yaml
# .github/workflows/dbt.yml
name: dbt Build & Test

on: [push, pull_request]

jobs:
  dbt:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"
      - name: Install dbt
        run: pip install dbt-bigquery
      - name: Run dbt build
        run: dbt build --target dev
```

- Runs models
- Executes tests
- Fails build if any test fails

---

## Best Practices

| Principle                             | Description                                      |
| ------------------------------------- | ------------------------------------------------ |
| **Test early and often**              | Add tests when creating models — don’t defer.    |
| **Fail loudly**                       | Bad data should block merges, not dashboards.    |
| **Keep tests modular**                | Test one thing per file or column.               |
| **Document everything**               | Every test should have a reason and description. |
| **Combine built-in and custom tests** | Balance coverage and maintainability.            |
| **Use `dbt build` in CI**             | Ensures models and tests are run in sequence.    |

## Example Folder Structure

```pgsql
dbt_project/
├── models/
│   ├── staging/
│   │   ├── stg_activities.sql
│   │   └── schema.yml
│   ├── marts/
│   │   ├── fct_activities.sql
│   │   └── dim_athletes.sql
│   └── schema.yml
├── tests/
│   ├── test_positive_distance.sql
│   ├── test_activity_vs_athlete.sql
│   └── test_no_null_names.sql
```

---

## Troubleshooting Common Issues

| Issue                           | Cause                            | Fix                                                  |
| ------------------------------- | -------------------------------- | ---------------------------------------------------- |
| “Test not found”                | Wrong YAML indentation           | Ensure tests are nested under `columns:`             |
| “Test failed but no rows shown” | Using ephemeral models           | Materialize upstream model or add `--store-failures` |
| “Relationship test too slow”    | Missing index or small dimension | Use incremental dimensions or limit test scope       |
| “Schema.yml ignored”            | Missing `version: 2` header      | Always include it                                    |

## Final Notes

- dbt tests are just SQL — easy to read, run, and debug.
- Testing is not optional; it’s how you guarantee trust in your models.
- Treat failing tests like broken code — fix upstream, not downstream.
- Combine testing, documentation, and CI for a self-healing data pipeline.

> “If it’s not tested, it’s not trusted.”
