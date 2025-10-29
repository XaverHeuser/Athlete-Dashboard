# dbt Snapshots

The **snapshots layer** tracks how data changes over time — giving you a historical view of records that evolve (like users, athletes, or configurations).  
Snapshots are the foundation of **Slowly Changing Dimensions (SCD Type 2)** and **auditing** use cases.

---

## Purpose

- Record **how and when** data changes in a source table.  
- Enable **historical analysis** (“what did we know at the time?”).  
- Support **Slowly Changing Dimensions (SCD Type 2)**.  
- Recreate **past states** of data for compliance or debugging.

> **Example:** If an athlete updates their weight or FTP, a snapshot keeps both the old and new values with valid-from/to timestamps.

---

## How Snapshots Work

When you run `dbt snapshot`, dbt:

1. Reads current source data.
2. Compares it to the **previous snapshot version**.
3. Inserts new rows for changed records.
4. Adds two timestamp columns:
   - `_dbt_valid_from` → when the record became active.
   - `_dbt_valid_to` → when the record was replaced (NULL if current).

Each time the source data changes, dbt records a new “version” of that row.

---

## Typical Snapshot Structure

```pgpql
snapshots/
├── athletes_snapshot.sql
├── equipment_snapshot.sql
└── schema.yml
```

---

## Example: Athlete Snapshot

```sql
-- snapshots/athletes_snapshot.sql

{% snapshot athletes_snapshot %}

{{
  config(
    target_schema='strava_snapshots',
    unique_key='athlete_id',
    strategy='timestamp',
    updated_at='updated_at',
    invalidate_hard_deletes=True
  )
}}

select
  athlete_id,
  name,
  sex,
  city,
  country,
  weight_kg,
  ftp,
  updated_at
from {{ source('strava_raw', 'athletes') }}

{% endsnapshot %}
```

This snapshot tracks changes in athlete attributes over time.

---

## Snapshot Strategies

| Strategy        | Description                                   | When to Use                                                               |
| --------------- | --------------------------------------------- | ------------------------------------------------------------------------- |
| **`timestamp`** | Compares based on a column like `updated_at`. | When your source includes a reliable `updated_at` or `modified_at` field. |
| **`check`**     | Compares all or specific columns for changes. | When no reliable timestamp exists or you need deep comparisons.           |

### Example: `check` strategy

```sql
{% snapshot equipment_snapshot %}
{{
  config(
    target_schema='strava_snapshots',
    unique_key='equipment_id',
    strategy='check',
    check_cols=['name', 'type', 'brand']
  )
}}

select
  id as equipment_id,
  name,
  type,
  brand,
  _ingested_at
from {{ source('strava_raw', 'equipment') }}
{% endsnapshot %}
```

---

## Resulting Table Schema

After running a snapshot, dbt creates a table like:

| Column                         | Description                                                 |
| ------------------------------ | ----------------------------------------------------------- |
| `athlete_id`                   | Natural key of the entity.                                  |
| `name`, `sex`, `country`, etc. | Attributes being tracked.                                   |
| `_dbt_valid_from`              | Timestamp when this record version became active.           |
| `_dbt_valid_to`                | Timestamp when this version was replaced (NULL if current). |
| `_dbt_snapshot_at`             | When dbt ran the snapshot.                                  |

---

## Usage

Run all snapshots:

```bash
dbt snaphost
```

dbt will:

- Compare current vs previous state.
- Identify any changed rows.
- Write updated records with new validity windows.

---

## Example Use Case

Let’s say an athlete updates their profile:

| athlete_id | name     | weight_kg | updated_at |
| ---------- | -------- | --------- | ---------- |
| 123        | Jane Doe | 65        | 2025-04-01 |
| 123        | Jane Doe | 68        | 2025-06-15 |

dbt will produce:

| athlete_id | weight_kg | _dbt_valid_from | _dbt_valid_to |
| ---------- | --------- | --------------- | ------------- |
| 123        | 65        | 2025-04-01      | 2025-06-15    |
| 123        | 68        | 2025-06-15      | NULL          |

You can now analyze historical metrics like weight-adjusted performance.

---

## Common Use Cases

| Use Case                   | Example                                    |
| -------------------------- | ------------------------------------------ |
| **Track profile changes**  | Athlete’s weight, FTP, or location.        |
| **Audit evolving records** | Strava activity corrections or deletions.  |
| **Maintain SCD Type 2**    | Customer or user attribute changes.        |
| **Regulatory compliance**  | “What did we know at the time?” scenarios. |
| **Debugging pipelines**    | Recreate the state of data at a past date. |

---

## Configuration Reference

| Config                    | Description                                  | Example              |
| ------------------------- | -------------------------------------------- | -------------------- |
| `target_schema`           | Schema (dataset) where snapshots are stored. | `'strava_snapshots'` |
| `unique_key`              | Natural key used to identify records.        | `'athlete_id'`       |
| `strategy`                | Comparison method (`timestamp` or `check`).  | `'timestamp'`        |
| `updated_at`              | Timestamp field for `timestamp` strategy.    | `'updated_at'`       |
| `check_cols`              | Columns to compare for `check` strategy.     | `['name', 'ftp']`    |
| `invalidate_hard_deletes` | Marks deleted source rows as invalid.        | `True`               |

---

## Best Practices

| Principle                      | Description                                                |
| ------------------------------ | ---------------------------------------------------------- |
| **Store snapshots separately** | Use a dedicated schema/dataset (e.g., `strava_snapshots`). |
| **Run snapshots regularly**    | Schedule daily or hourly in CI/CD.                         |
| **Use incremental loading**    | dbt handles only changes since the last run.               |
| **Keep `unique_key` stable**   | Changing it breaks historical continuity.                  |
| **Add snapshot tests**         | Validate uniqueness and continuity.                        |
| **Don’t over-snapshot**        | Only track entities that change meaningfully.              |

---

## Example Snapshot Tests

Define tests in ``schema.yml` for snapshots, too:

```yaml
version: 2

snapshots:
  - name: athletes_snapshot
    description: 'Tracks historical attribute changes for each athlete.'
    columns:
      - name: athlete_id
        tests:
          - not_null
          - unique
      - name: _dbt_valid_from
        tests:
          - not_null
```

---

## Querying Snapshot Data

To get the current record version:

```sql
select *
from {{ ref('athletes_snapshot') }}
where _dbt_valid_to is null
```

To analyze historical states:

```sql
select *
from {{ ref('athletes_snapshot') }}
where '2025-04-15' between _dbt_valid_from and coalesce(_dbt_valid_to, current_timestamp())
```

---

## CI/CD Integration

Add a nightly snapshot job to your CI/CD pipeline.

### Example GitHub Actions step

```yaml
- name: Run dbt snapshots
  run: dbt snapshot --target prod
```

You can also chain it with your build:

```yaml
dbt build && dbt snapshot
```

---

## Folder & Dataset Structure

```graphql
dbt_project/
├── snapshots/
│   ├── athletes_snapshot.sql
│   ├── equipment_snapshot.sql
│   └── schema.yml
├── models/
│   ├── staging/
│   ├── marts/
│   └── ...
└── dbt_project.yml
```

In BigQuery:

```graphql
strava_snapshots/
  ├── athletes_snapshot
  └── equipment_snapshot
```

---

## Final Notes

- Snapshots make your dbt project time-aware — you can always see what changed, when, and why.
- They are essential for auditing, historical KPIs, and regulatory tracking.
- Use snapshots for dimensions that evolve, not static data.
- Keep them light and focused — they grow over time.

> “dbt snapshots are your time machine — don’t build without one.”
