# dbt (data build tool) - Overview

- dbt (data build tool) lets you transform, test, and document data directly inside your warehouse (like BigQuery).
- It helps you build reliable, modular data pipelines using SQL and YAML — with version control and CI/CD integration.

## schema.yml

### What it is

This file — usually named schema.yml or models/staging/schema.yml — is a dbt resource definition file.
It’s written in YAML and serves three major purposes:

- Documentation — defines what your models and columns mean
- Testing — defines what data quality checks dbt should run
- Lineage & metadata — connects models, sources, and downstream dependencies in dbt’s DAG

### Version header

This tells dbt which syntax version of YAML structure is being used (v2 is current).
Without it, dbt wouldn’t know how to interpret your resource definitions.

### The models section

```yaml
models:
  - name: staging_activities
    description: "{{ doc('staging_activities__doc') }}"
```

- **models**: defines metadata for dbt models (files like staging_activities.sql).
- Each item under it (- name: ...) corresponds to one model in your project.
- **description**: gives a human-readable description.
- Here, it references a markdown doc block ({{ doc('...') }}) defined in a separate docs.md file for richer documentation.

### The column section

```yaml
columns:
  - name: activity_id
    description: "Unique identifier for each activity."
    tests:
      - not_null
      - unique
```

This describes each column in your model:

| Property      | Description                                             |
| ------------- | ------------------------------------------------------- |
| `name`        | Must match the column name in your SQL model.           |
| `description` | Visible in dbt docs and lineage graph.                  |
| `tests`       | dbt runs these as SQL queries to validate data quality. |


### Usage

Run tests:

```bash
dbt test
```

dbt will:
1. Parse all schema.yml and sources.yml files
2. Generate SQL test queries automatically
3. Execute them in your data warehouse (e.g., BigQuery)
4. Report pass/fail results in your terminal or CI pipeline

For example:

```yaml
tests:
  - not_null
```
becomes a query like:
```sql
select *
from athlete-dashboard-467718.strava_data.staging_activities
where activity_id is null;
```
- If any rows are returned → test fails ❌
- If none → test passes ✅


### Types of Test

#### Built-in Tests

| Test                            | Purpose                                                                          | Example YAML                                                                                                                         | Example SQL it generates                                                            |
| ------------------------------- | -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| **`not_null`**                  | Ensures a column never contains NULLs.                                           | `yaml - not_null `                                                                                                                   | `sql select * from table where column is null; `                                    |
| **`unique`**                    | Ensures values in a column are unique.                                           | `yaml - unique `                                                                                                                     | `sql select column, count(*) from table group by column having count(*) > 1; `      |
| **`accepted_values`**           | Ensures column values are within a predefined list.                              | `yaml - accepted_values: arguments: values: ['Ride', 'Run', 'Swim']`                                                                 | `sql select * from table where column not in ('Ride','Run','Swim'); `               |
| **`relationships`**             | Validates referential integrity between models/sources (foreign key check).      | `yaml - relationships: arguments: to: ref('dim_athletes') field: athlete_id `                                                        | `sql select * from child where athlete_id not in (select athlete_id from parent); ` |
| **`not_accepted_values`**       | Fails if the column contains *disallowed* values (inverse of `accepted_values`). | `yaml - not_accepted_values: arguments: values: ['Error', 'Unknown'] `                                                               | `sql select * from table where column in ('Error', 'Unknown'); `                    |
| **`expression_is_true`**        | Checks that a given boolean expression holds true for all rows.                  | `yaml - expression_is_true: arguments: expression: "distance_m >= 0" `                                                               | `sql select * from table where not (distance_m >= 0); `                             |
| **`conditional_values`**        | Validates data only when a condition is met.                                     | `yaml - conditional_values: arguments: condition: "sport_type = 'Run'" expression: "avg_speed_mps > 0" `                             | Runs test only on filtered subset of rows.                                          |
| **`mutually_exclusive_ranges`** | Ensures no overlapping ranges exist between start/end columns.                   | `yaml - mutually_exclusive_ranges: arguments: lower_bound_column: start_date upper_bound_column: end_date partition_by: athlete_id ` | Validates intervals don’t overlap for same partition key.                           |
| **`non_overlapping_ranges`**    | Similar to above; checks chronological ordering or exclusive intervals.          | `yaml - non_overlapping_ranges: arguments: lower_bound_column: valid_from upper_bound_column: valid_to `                             | Ensures date ranges don’t overlap.                                                  |

#### Custom Tests

Create a file under tests/, e.g. tests/test_positive_distance.sql:
```sql
-- tests/test_positive_distance.sql
select *
from {{ ref('staging_activities') }}
where distance_m < 0
```
If any rows are returned, dbt marks it as a FAIL.
Run:
```bash
dbt test --select test_positive_distance
```

### Documentation in action

When you run:
```bash
dbt docs generate
dbt docs serve
```
dbt creates a web app (by default at http://localhost:8080) showing:
- Model names and descriptions
- Column-level docs
- Relationships to sources and downstream models
- Test results and metadata
This turns your YAML into a living data catalog.


### Why it matters

Having a rich *schema.yml* like yours:
- Enables automatic testing (data quality guardrails)
- Powers auto-generated documentation for your models
- Keeps your project self-explanatory and auditable
- Makes dbt aware of your semantic layer — what each field means and how it should behave



## Snapshots

- Snapshots let you track changes in your source data over time — perfect for slowly changing dimensions (SCD Type 2) or history tables.
- They compare current data in your source with the last version stored by dbt, and record any differences automatically.

### Example

- target_schema: BigQuery dataset for snapshots (created automatically)
- unique_key: Natural key for your source table (e.g., id)
- strategy:
    - 'check': compare all column values for changes
    - 'timestamp': compare a specific column (like updated_at)
- check_cols: Which columns to monitor ('all' or list of column names)

### Usage

Run:

```bash
dbt snapshot
```

dbt will:

1. Compare your current source data against the previous snapshot version.
2. Record any changed rows with:
    - _dbt_valid_from → when the record became active
    - _dbt_valid_to → when it was replaced (null if current)
3. Write new/changed records to your snapshot table.

### When to use Snapshot

| Use Case                           | Example                                          |
| ---------------------------------- | ------------------------------------------------ |
| Track historical attribute changes | Athlete’s FTP, weight, or club membership        |
| Audit evolving records             | Strava activity updates or corrections           |
| SCD Type 2 tables                  | Customer, athlete, or activity dimension changes |
| Regulatory auditing                | “What did we know at the time?” scenarios        |

### Why Snapshot Matter

- Capture historical context for analysis (“what changed, when”)
- Enable Slowly Changing Dimension (SCD Type 2) logic
- Help audit or debug pipelines by reconstructing prior states
- Ideal for mutable APIs like Strava, Salesforce, HubSpot, etc.

### Best Practices

- Store snapshots in a separate dataset (e.g., strava_snapshots)
- Schedule dbt snapshot nightly or hourly via CI/CD
- Use strategy: timestamp if your source provides an updated_at
- Add tests: to your snapshot table too — it behaves like any other dbt model
