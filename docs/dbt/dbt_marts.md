# dbt Marts Layer

The **marts layer** is where your clean staging data becomes **business-ready analytics models**.  
This is where the real data modeling happens — defining **facts**, **dimensions**, and **reports** that represent your business entities and metrics.

---

## Purpose

The marts layer transforms curated staging data into:

- **Facts** — measurable business events.
- **Dimensions** — descriptive context for facts.
- **Reports** — aggregated, BI-ready views.

> Think: *“What questions do analysts or dashboards need to answer?”*

---

## Core Principles

| Rule | Description |
|------|--------------|
| **1️⃣  Use only clean data** | Always source from `stg_` models, never raw sources. |
| **2️⃣  Define grain explicitly** | Each fact/dimension must clearly define “1 row = X”. |
| **3️⃣  Separate facts, dimensions, and reports** | Keep model purposes distinct and modular. |
| **4️⃣  Reuse existing models** | Use `ref()` to connect staging and lower-level marts. |
| **5️⃣  Avoid double transformations** | No cleaning or standardization here — that’s staging’s job. |
| **6️⃣  Keep naming consistent** | Prefix with `fct_`, `dim_`, or `rpt_`. |
| **7️⃣  Be performance-aware** | Use incremental models or partitions for large tables. |

---

## Marts Layers Overview

| Layer | Prefix | Purpose | Granularity | Example |
|--------|--------|----------|--------------|----------|
| **Facts** | `fct_` | Quantitative events and metrics. | 1 row = event (e.g. activity, order) | `fct_activities`, `fct_orders` |
| **Dimensions** | `dim_` | Descriptive entities providing context. | 1 row = entity (athlete, customer) | `dim_athletes`, `dim_customers` |
| **Reports** | `rpt_` | Aggregated, BI-ready data. | 1 row = time or category summary | `rpt_activity_summary`, `rpt_revenue_daily` |

---

## Facts

**Facts** capture measurable business events — things that happen and can be counted or summed.

### Guidelines Fct

| Principle | Description |
|------------|--------------|
| **1 row = 1 event** | Define the grain clearly. |
| **Include foreign keys** | Link to related dimensions (`athlete_id`, `equipment_id`). |
| **Include measures** | Quantitative metrics (distance, duration, revenue, etc.). |
| **No derived aggregates** | Keep metrics atomic; aggregates go into reports. |
| **Materialize as table** | Facts are core data — store for performance. |

### Example Fct

```sql
-- models/marts/fct_activities.sql
/*
1 row = 1 Strava activity
Captures key metrics and attributes for performance analysis.
*/

with base as (
  select *
  from {{ ref('stg_activities') }}
),

joined as (
  select
    b.activity_id,
    b.athlete_id,
    b.activity_type,
    b.start_datetime_utc,
    b.distance_m,
    b.moving_time_s,
    b.avg_speed_mps,
    b.avg_heartrate_bpm,
    b.max_heartrate_bpm,
    {{ ref('dim_athletes') }}.age as athlete_age,
    {{ ref('dim_athletes') }}.sex as athlete_sex
  from base b
  left join {{ ref('dim_athletes') }}
    on b.athlete_id = {{ ref('dim_athletes') }}.athlete_id
)

select * from joined
```

### schema.yml

```yaml
version: 2

models:
  - name: fct_activities
    description: 'Fact table representing individual Strava activities.'
    columns:
      - name: activity_id
        description: 'Unique identifier for each activity.'
        tests:
          - not_null
          - unique
      - name: athlete_id
        description: 'Foreign key to dim_athletes.'
        tests:
          - relationships:
              to: ref('dim_athletes')
              field: athlete_id
```

---

## Dimensions

Dimensions describe the who, what, where, and when of your data.
They provide attributes used to group and filter facts.

### Guidelines Dim

| Principle                   | Description                                                   |
| --------------------------- | ------------------------------------------------------------- |
| **1 row = 1 entity**        | Define a stable primary key.                                  |
| **Descriptive fields only** | No metrics or derived measures.                               |
| **Joinable via keys**       | Match key types with facts (e.g., `athlete_id` as INT64).     |
| **Slowly changing logic**   | Use snapshots or latest-record logic for historical accuracy. |
| **Materialize as table**    | Typically static or slowly changing.                          |

### Example Dim

```sql
-- models/marts/dim_athletes.sql
/*
1 row = 1 athlete
Provides descriptive details about each athlete.
*/

with base as (
  select *
  from {{ ref('stg_athletes') }}
)

select
  athlete_id,
  name,
  sex,
  city,
  country,
  weight_kg,
  height_cm,
  first_activity_date,
  last_activity_date
from base
```

---

## Reports

Reports (or aggregations) summarize fact data for dashboards and BI tools.
They provide time-based or category-level metrics.

### Guidelines Rep

| Principle                               | Description                                        |
| --------------------------------------- | -------------------------------------------------- |
| **Aggregated facts**                    | Built on `fct_` models.                            |
| **Time-based granularity**              | Daily, weekly, monthly.                            |
| **Include derived KPIs**                | Average pace, total distance, etc.                 |
| **BI-ready naming**                     | Clear metric labels, user-friendly column names.   |
| **Materialize as table or incremental** | Large tables should be partitioned or incremental. |

### Example Rep

```sql
-- models/marts/rpt_activity_summary.sql
/*
1 row = 1 athlete per week
Summarized KPIs for performance reporting.
*/

with base as (
  select *
  from {{ ref('fct_activities') }}
),

aggregated as (
  select
    athlete_id,
    date_trunc(start_datetime_utc, week) as week_start,
    count(*) as total_activities,
    sum(distance_m) / 1000 as total_distance_km,
    sum(moving_time_s) / 3600 as total_time_h,
    avg(avg_speed_mps) * 3.6 as avg_speed_kmh
  from base
  group by 1, 2
)

select * from aggregated
```

---

## Materialization Strategy

| Model Type    | Recommended Materialization | Notes                              |
| ------------- | --------------------------- | ---------------------------------- |
| **Fact**      | `table`                     | Fast access for repeated joins.    |
| **Dimension** | `table`                     | Usually stable or slowly changing. |
| **Report**    | `table` or `incremental`    | For large data volumes.            |

> Define materializations in dbt_project.yml or per-model configs.

Example per-model config:

```sql
{{ config(materialized='table') }}
```

---

## Performance Tips

- Use CTEs sparingly in large aggregations — materialize intermediate steps if needed.
- Partition large fact tables by date for efficiency.
- Limit report scope (e.g., last 2 years) to keep queries fast.
- Use incremental models when data arrives append-only.
- Pre-aggregate in reports — BI tools shouldn’t have to re-sum billions of rows.

---

## Example Folder Structure

```pgsql
models/
├── marts/
│   ├── facts/
│   │   ├── fct_activities.sql
│   │   └── fct_orders.sql
│   ├── dimensions/
│   │   ├── dim_athletes.sql
│   │   └── dim_customers.sql
│   ├── reports/
│   │   ├── rpt_activity_summary.sql
│   │   └── rpt_revenue_daily.sql
│   └── schema.yml
```

---

## Model Checklist

- Model name prefixed with fct_, dim_, or rpt_
- Uses only {{ ref('stg_*') }} or other marts models — no raw tables
- Clearly defines “1 row = X”
- Includes a schema.yml with descriptions and tests
- Aggregations only appear in report models
- Materialized appropriately (table or incremental)
- Includes primary key and foreign keys for lineage

---

## Final Notes

- Facts = actions, Dimensions = context, Reports = insights.
- Keep transformations modular and clearly separated by purpose.
- Build your marts to be readable by analysts and reliable for BI.
- Every fact and dimension should trace back to a documented, tested source.

> “Clean staging makes facts reliable; clear facts make insights possible.”
