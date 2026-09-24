# Data Manipulation (Snowflake)

This stage loads the cleaned CSV into Snowflake and builds a set of
pre-aggregated summary tables that answer each business question directly —
so the Power BI dashboard queries small, ready-made tables instead of
aggregating raw rows on every refresh.

All DDL/DML is in [`snowflake_queries.sql`](snowflake_queries.sql).

## What's in the database

| Table | Answers | Grain |
|---|---|---|
| `STARTUP_FUNDING` | Base table, loaded from `data/processed/Start-Up_funding_cleaned.csv` | 1 row per funding record |
| `TOTAL_FUNDING_INDIA` | Total funding in India, per year (excludes rows where `City_Location` is actually a foreign city) | 1 row per year |
| `TOTAL_FUNDING` | Overall funding per year (all rows) | 1 row per year |
| `TOTAL_CONSUMER_INTERNET` | Count of Consumer Internet companies per year | 1 row per year |
| `TOTAL_CONSUMER_INTERNET_FUNDING` | Funding amount per Consumer Internet company | 1 row per company |
| `TOTAL_COMPANIES_ABOVE_500000` | Count of companies funded above USD 500,000, per year | 1 row per year |
| `COMPANIES_BY_CITY` | Spread of all funded companies across cities | 1 row per city |
| `CONSUMER_INTERNET_BY_CITY` | Spread of Consumer Internet companies across cities | 1 row per city |
| `SEED_FUNDING_BY_YEAR` | Count and total of Seed-funded companies, per year | 1 row per year |

## Performance tuning

- Used an `XSMALL` warehouse with `AUTO_SUSPEND`/`AUTO_RESUME` to control
  credit usage for a dataset of this size (~2,000 rows).
- Pre-aggregated result tables instead of letting Power BI aggregate on the
  fly, so the dashboard hits small, ready-made summary tables rather than
  scanning/grouping the raw table on every query.
- A clustering key on `(INDUSTRY_VERTICAL, DATE)` was considered for the
  base table, should it grow beyond a single micro-partition.

## Run it

```sql
-- In a Snowflake worksheet, with the right role/warehouse selected:
!source snowflake_queries.sql
```

Or paste the contents of `snowflake_queries.sql` into a Snowflake worksheet
and run it top to bottom. It creates the database/warehouse, the base table,
and all nine summary tables above.
