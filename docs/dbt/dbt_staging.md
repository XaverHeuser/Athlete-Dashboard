# dbt Staging Layer

The **staging layer** is where raw source data becomes **clean, reliable, and standardized**.  
It’s the foundation for all downstream models — facts, dimensions, and reports.

---

## Purpose

Staging models:

- Clean and rename raw data fields.
- Fix data types and formats.
- Standardize naming conventions.
- Remove duplicates and invalid rows.
- Add lightweight derived fields.
- Define join keys and relationships.

> **Goal:** Make raw data usable — not analytical yet.

---

## Core Principles

| Rule | Description |
|------|--------------|
| **One model per raw table** | Keep 1:1 mapping between raw source and staging model. |
| **Same granularity as source** | Don’t aggregate or group data. |
| **Keep transformations simple** | Rename, cast, clean — no business logic. |
| **Use consistent naming** | Prefix models with `stg_`. |
| **Reuse logic with macros** | Don’t repeat cleaning logic; define reusable Jinja macros. |
| **Materialize as views** | Staging is lightweight and should stay dynamic. |

---

## Typical Transformations

| Step | Transformation | Example |
|------|----------------|----------|
| 1️⃣ | **Rename columns** | `orderId → order_id`, `userName → customer_name` |
| 2️⃣ | **Fix data types** | `CAST(order_date AS TIMESTAMP)` |
| 3️⃣ | **Standardize time zones** | Convert all timestamps to UTC |
| 4️⃣ | **Clean string fields** | `TRIM(LOWER(email))` |
| 5️⃣ | **Deduplicate records** | Keep latest per unique key |
| 6️⃣ | **Filter invalid data** | Exclude test users, null IDs |
| 7️⃣ | **Flatten JSON / nested data** | Extract nested JSON fields |
| 8️⃣ | **Add audit fields** | `_ingested_at`, `_source_file` |
| 9️⃣ | **Add simple derived columns** | `is_new_customer = order_date = first_order_date` |

---

## Example: Staging Model (Strava Activities)

```sql
-- models/staging/stg_activities.sql
/*
1 row = 1 raw Strava activity
Cleans and standardizes raw Strava activity data.
*/

with source as (
  select * from {{ source('strava_raw', 'activities') }}
),

renamed as (
  select
    id as activity_id,
    athlete_id,
    name as activity_name,
    type as activity_type,
    start_date as start_datetime_utc,
    moving_time as moving_time_s,
    elapsed_time as elapsed_time_s,
    distance as distance_m,
    average_speed as avg_speed_mps,
    max_speed as max_speed_mps,
    average_heartrate as avg_heartrate_bpm,
    max_heartrate as max_heartrate_bpm,
    _ingested_at
  from source
  where athlete_id is not null
)

select * from renamed
```

## Example schema.yml

```yaml
version: 2

models:
  - name: stg_activities
    description: "Cleaned and standardized Strava activity data."
    columns:
      - name: activity_id
        description: "Unique identifier for each activity."
        tests:
          - not_null
          - unique
      - name: athlete_id
        description: "Foreign key linking to the athlete dimension."
        tests:
          - not_null
```

> Add a `schema.yml` in every staging folder for documentation and tests.

---

## Key Design Patterns

### Always define “1 row = X”

Every model should make its granularity explicit in a comment:

```sql
-- 1 row = 1 raw activity event
```

### Never aggregate

Aggregation belongs in marts (fct_, rpt_), not staging.

### Don’t join across sources

If you need to combine data from multiple sources, do that in intermediate or fact models.

### Keep transformations idempotent

Staging models should produce the same output every run.

---

## File Structure Example

```pgsql
models/
├── staging/
│   ├── stg_activities.sql
│   ├── stg_athletes.sql
│   ├── stg_equipment.sql
│   └── schema.yml
```

- One `.sql` file per source table.
- One shared `schema.yml` per folder.

---

## Jinja & Macros for Staging

Use macros to avoid repeating common cleaning logic.

### Example jinja

```jinja
-- macros/clean_string.sql
{% macro clean_string(field) %}
  trim(lower({{ field }}))
{% endmacro %}
```

### Usage jinja

```sql
select
  {{ clean_string('email') }} as email_cleaned
from {{ source('raw', 'users') }}
```

---

## Materialization

Default to views unless:

- The dataset is large or reused heavily → then table.
- You’re staging an external API source with slow queries.

Configure globally or per-model:

```yaml
models:
  staging:
    +materialized: view
```

---

## Staging Checklist

- Model named with `stg_` prefix
- 1 model = 1 raw source
- Uses `{{ source() }}` not hardcoded paths
- All columns renamed, typed, and cleaned
- No aggregations or joins
- Has `schema.yml` with tests + descriptions
- Materialized as view

---

## Final Notes

- The staging layer is where data quality starts — clean once, use everywhere.
- Build from sources → staging → marts in clear steps.
- Keep staging simple, transparent, and reproducible.

> “If your staging is clean, your marts stay sane.”
