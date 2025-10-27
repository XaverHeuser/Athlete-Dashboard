# dbt Guidelines & Best Practices

This document defines **how we structure, name, and design models** in our dbt project.  
Following these guidelines ensures consistency, clarity, and scalability — especially as the number of models grows.

---

## 🎯 Purpose

- Maintain **clean, readable, and predictable** model structures.
- Keep a clear **data lineage** between layers.
- Simplify onboarding and debugging.
- Enable seamless integration with BI tools and analytics layers.

---

## 🧱 Core Modeling Principles

| Guideline | Description |
|------------|--------------|
| **1. Define “1 row = X”** | Always specify what a single row represents in every model. |
| **2. One model = one purpose** | Avoid mixing raw, cleaned, and aggregated logic in a single model. |
| **3. Reuse lower-level models** | Build modularly — use `ref()` to chain transformations step-by-step. |
| **4. Keep business logic isolated** | Transformations belong in marts (facts/dims), not staging. |
| **5. Final tables = BI-ready** | Facts and reports should be directly usable for analytics. |
| **6. Keep naming clear and consistent** | Prefix models based on layer (`stg_`, `fct_`, `dim_`, `rpt_`). |
| **7. Test and document everything** | Every key column should have `not_null` and `unique` tests. |
| **8. Simplicity > cleverness** | Avoid unnecessary CTEs or Jinja complexity — clarity first. |

---

## 🏗️ Model Layering

Our dbt project is organized in **four conceptual layers**.  
Each layer has a clear purpose, naming convention, and granularity.

| Layer | Prefix | Purpose | Granularity | Example Models |
|--------|--------|----------|--------------|----------------|
| **Staging** | `stg_` | Clean and standardize raw data. | 1 row = source record | `stg_activities`, `stg_athletes` |
| **Facts** | `fct_` | Core transactional tables with metrics. | 1 row = event/transaction | `fct_activities`, `fct_orders` |
| **Dimensions** | `dim_` | Descriptive tables about entities. | 1 row = entity (athlete, customer, etc.) | `dim_athletes`, `dim_customers` |
| **Reports** | `rpt_` | Aggregated data for BI dashboards. | 1 row = date, category, or summary unit | `rpt_activity_summary`, `rpt_revenue_daily` |

See [dbt Staging](./dbt_staging.md) and [dbt Marts](./dbt_marts.md) for detailed implementation examples.

---

## 🧾 Naming Conventions

### ✅ Models

| Layer | Prefix | Example |
|--------|--------|----------|
| Staging | `stg_` | `stg_orders` |
| Facts | `fct_` | `fct_sales` |
| Dimensions | `dim_` | `dim_products` |
| Reports | `rpt_` | `rpt_sales_summary` |
| Intermediate | `int_` *(optional)* | `int_customer_behavior` |

> **Tip:** Avoid using project- or schema-specific names in model files (e.g., don’t include `raw_` or `analytics_` in filenames).

---

### ✅ Columns

- Use **snake_case** for all column names.  
  
  ```sql
  select
    order_id,
    customer_id,
    order_date
  from ...
  ```

- Prefer clear, descriptive names over abbreviations (athlete_id > ath_id).
- Prefix or suffix derived metrics if needed (distance_m, avg_speed_mps).
- Align naming conventions with your BI layer (for seamless handoff).

## File & Folder Naming

| Type         | Convention           | Example                            |
| ------------ | -------------------- | ---------------------------------- |
| Folder       | Lowercase, no spaces | `models/staging/`, `models/marts/` |
| Model files  | Match model name     | `stg_activities.sql`               |
| Schema files | One per folder       | `schema.yml`                       |
| Test files   | snake_case           | `test_positive_distance.sql`       |

## Dependencies and ref() Usage

- Always reference upstream models via {{ ref('model_name') }} — never hardcode schema.table.
- This enables dbt to:
  - Build dependency DAGs.
  - Run models in the correct order.
  - Track lineage in docs.
- For external sources, use {{ source('source_name', 'table_name') }}.

Example_

```sql
select
  a.athlete_id,
  a.name,
  act.total_distance_m
from {{ ref('dim_athletes') }} as a
join {{ ref('fct_activities') }} as act
  on a.athlete_id = act.athlete_id
```

## Materialization Rules

| Layer          | Recommended Materialization | Notes                            |
| -------------- | --------------------------- | -------------------------------- |
| **Staging**    | `view`                      | Light transformations only.      |
| **Facts**      | `table`                     | Persist metrics for performance. |
| **Dimensions** | `table`                     | Low update frequency.            |
| **Reports**    | `table` or `incremental`    | Aggregated data; may be large.   |
| **Snapshots**  | `table`                     | Automatically managed by dbt.    |

Define this in dbt_project.yml or inside model configs:

```yaml
models:
  +materialized: view
```

## Jinja & Macros

Use Jinja templates and macros for reusable logic, but avoid overengineering.

Example macro:

```jinja
-- macros/clean_string.sql
{% macro clean_string(column_name) %}
    trim(lower({{ column_name }}))
{% endmacro %}
```

Usage:

```sql
select
  {{ clean_string('email') }} as email_cleaned
from {{ ref('stg_customers') }}
```

## Testing & Documentation Standards

Every model must have a corresponding schema.yml file that defines:

- Model-level description
- Column-level descriptions
- Tests (e.g., not_null, unique, etc.)

Example:

```yaml
version: 2
models:
  - name: stg_activities
    description: "Cleans and standardizes raw Strava activity data."
    columns:
      - name: activity_id
        description: "Unique identifier for each activity."
        tests:
          - not_null
          - unique
```

See [dbt Testing](./dbt_testing.md) for more.

## Example Transformation Flow

```text
raw.activities
   ↓
stg_activities          (clean, rename, cast)
   ↓
fct_activities          (add metrics like pace, duration)
   ↓
dim_athletes            (descriptive dimension)
   ↓
rpt_activity_summary    (aggregate per athlete, per week)
```

Each model layer adds value while maintaining clear separation of responsibility.

## CI/CD & Version Control

| Topic                | Best Practice                                             |
| -------------------- | --------------------------------------------------------- |
| **Git**              | Commit all SQL + YAML files. Use branches for new models. |
| **Pull Requests**    | Run `dbt build` or `dbt test` in CI before merging.       |
| **Docs**             | Regenerate docs on each merge (`dbt docs generate`).      |
| **Freshness checks** | Automate `dbt source freshness` via CI/CD.                |
| **Environments**     | Use `dev`, `prod` datasets via `profiles.yml`.            |

## Example Checklist for New Models

- Define “1 row = X” in the model header comment
- Use ref() instead of hardcoded table names
- Write a clear model description in schema.yml
- Add not_null and unique tests for key fields
- Ensure naming matches layer prefix convention
- Commit both .sql and .yml files together

## Related Docs

| Topic                                 | Description                                |
| ------------------------------------- | ------------------------------------------ |
| [dbt Guidelines](./dbt_guidelines.md) | Core modeling rules and naming conventions |
| [dbt Staging](./dbt_staging.md)       | How to build clean staging models          |
| [dbt Marts](./dbt_marts.md)           | Facts, dimensions, and reporting models    |
| [dbt Testing](./dbt_testing.md)       | Schema.yml structure and data tests        |
| [dbt Snapshots](./dbt_snapshots.md)   | Capturing historical changes               |
| [dbt Profiles](./dbt_profiles.md)     | Connecting dbt to BigQuery                 |

## Final Notes

- dbt thrives on clarity and modularity — fewer, smaller models > giant SQL scripts.
- Your dbt DAG is a reflection of your logic — keep it simple and traceable.
- Remember: clarity scales, complexity breaks.

“In dbt, models are code. Treat them like code — reviewed, tested, and documented.”
