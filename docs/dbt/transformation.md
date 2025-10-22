# Some help for dbt

## Guidelines

| Rule                        | Description                                          |
| --------------------------- | ---------------------------------------------------- |
| Define row meaning       | “1 row = X” → the most important question            |
| One model = one purpose  | Don’t mix raw, cleaned, and aggregated data          |
| Reuse lower-level models | Use `ref()` to build logically, step by step         |
| Final tables = BI ready  | Pre-aggregated for dashboards, if needed             |
| Keep naming clear        | `stg_`, `fct_`, `dim_`, `rpt_` — consistent prefixes |


## Example Naming Hierarchy

| Layer          | Example Tables                | Granularity           |
| -------------- | ----------------------------- | --------------------- |
| **Staging**    | `stg_orders`, `stg_customers` | 1 row = source record |
| **Facts**      | `fct_orders`                  | 1 row = order         |
| **Dimensions** | `dim_customers`               | 1 row = customer      |
| **Reports**    | `rpt_revenue_daily`           | 1 row = day           |



```sql
raw.orders  ─────────────┐
                         │
stg_orders               │  → clean + renamed
                         ↓
fct_orders ──────────────┤  → one order per row, with metrics
                         ↓
rpt_orders_daily          → aggregated by day for reporting
```

```sql
raw.orders      → 1 row = source event
stg_orders      → 1 row = clean order
fct_orders      → 1 row = order with metrics
rpt_orders_daily → 1 row = day
```


## Main Goals of the Staging Layer

| Goal                                   | Description                                         |
| -------------------------------------- | --------------------------------------------------- |
| 🧹 **Clean the data**                  | Fix types, remove duplicates, handle nulls          |
| 🧾 **Standardize naming**              | Rename ugly source fields → clear business names    |
| 🧮 **Add lightweight derived columns** | Parse timestamps, flags, or normalize text          |
| 🔗 **Define relationships**            | Add keys that can be used to join across datasets   |
| 🪶 **Keep it simple**                  | No heavy business logic — just make raw data usable |


## Typical Transformations in Staging

| Step | Transformation                        | Example                                                 |
| ---- | ------------------------------------- | ------------------------------------------------------- |
| 1️⃣  | **Rename columns**                    | `orderId` → `order_id`, `userName` → `customer_name`    |
| 2️⃣  | **Fix data types**                    | `CAST(order_date AS TIMESTAMP)`                         |
| 3️⃣  | **Standardize timestamps/time zones** | Convert to UTC or warehouse default                     |
| 4️⃣  | **Clean string fields**               | `TRIM(LOWER(email))`, remove extra spaces               |
| 5️⃣  | **Deduplicate records**               | Keep the latest record per unique key                   |
| 6️⃣  | **Filter out bad data**               | Drop test users, incomplete rows, etc.                  |
| 7️⃣  | **Flatten JSON/nested fields**        | Extract nested JSON into columns                        |
| 8️⃣  | **Add audit columns**                 | e.g., `_ingested_at`, `_source_file`, `_row_number`     |
| 9️⃣  | **Basic derived fields**              | e.g., `is_new_customer = order_date = first_order_date` |

- Rule of thumb:
    - If a transformation is source-specific or cleanup-related, do it here.
    - If it’s business logic, do it later (in marts).

## Staging Model Best Practices

| Principle                      | Example                                |
| ------------------------------ | -------------------------------------- |
| **1 model per raw table**      | `stg_customers`, `stg_orders`          |
| **Same granularity as source** | Don’t aggregate                        |
| **Only light transformations** | Rename, cast, clean                    |
| **Use Jinja macros**           | Reuse logic like `clean_string(field)` |
| **Keep naming consistent**     | `stg_<source_table>`                   |
| **Materialize as views**       | Unless very large or reused often      |

