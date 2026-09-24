# Data

This folder holds every stage of the dataset, from the raw export handed
over by the client to the final, analysis-ready file loaded into Snowflake.
See [`../data_cleaning/`](../data_cleaning/) for the script that reproduces
every stage below.

```
data/
├── raw/
│   ├── Start-up_Funding1.csv   # Stage 1 — raw export (as received)
│   ├── Start-up_Funding2.csv   # Stage 2 — columns split
│   └── Start-Up_Funding.csv    # Stage 3 — unwanted characters removed
└── processed/
    └── Start-Up_funding_cleaned.csv   # Stage 4 — final, analysis-ready file
```

## File-by-file: what was done, and why

### 1. `raw/Start-up_Funding1.csv` — the raw data as given
This is the file exactly as it was exported/received. It is **not usable
as-is**: every record is squashed into a single quoted field, wrapped in an
extra pair of quotes, and terminated with a stray `||` artifact, e.g.

```
"1,12/12/19,Ecozen,Technology,Agritech,Pune,Sathguru Catalyzer Advisors,Series A,""60,00,000"",""||
```

It also carries a UTF-8 byte-order mark (BOM) on the header line. 3,037 data rows.

### 2. `raw/Start-up_Funding2.csv` — columns split
The `||` artifact and the outer quote-wrapping were stripped, and each line
was re-parsed as proper CSV, splitting it into the 10 real columns:
`Sr No, Date dd/mm/yyyy, Startup Name, Industry Vertical, Sub Vertical,
City Location, Investors Name, Investment Type, Amount in USD, Remarks`.

The data is now tabular, but still "dirty":
- Mixed date separators and formats (`12/12/19`, `12.05.2015`, `01/07/2015`)
- Encoding artifacts in text fields (mis-decoded apostrophes, e.g. `Byju's`
  showing up as escaped byte sequences)
- Inconsistent spelling of the same category (`Ecommerce`, `eCommerce`,
  `E-Commerce`)
- Multi-value fields still contain internal commas (e.g. an `Investors Name`
  of `"Mumbai Angels, Ravikanth Reddy"`)
- `Amount in USD` still has Indian-style digit grouping (`5,00,00,000`) and
  occasional stray `+` characters

### 3. `raw/Start-Up_Funding.csv` — unwanted characters removed
A text-cleanup pass was applied to the columns most likely to break a naive
`,`-delimited read or a `GROUP BY`:

- **Investors Name / Industry Vertical / Sub Vertical / City Location** —
  internal commas removed (e.g. `"Mumbai Angels, Ravikanth Reddy"` →
  `"Mumbai Angels Ravikanth Reddy"`), so a single record with several
  investors/categories reads as one clean value instead of colliding with
  the CSV delimiter.
- **Spelling standardized** — `Ecommerce` / `eCommerce` → `E-commerce`.
- **Encoding artifacts fixed** — mis-decoded punctuation restored (e.g.
  `Byju's`).
- **Dates standardized** — separators normalized to `-` (`12/12/19` →
  `12-12-2019` style).
- Stray leading/trailing whitespace trimmed across all columns.

`Amount in USD` and `Remarks` are still present in raw form at this stage —
those are handled in the next (Python/pandas) step.

### 4. `processed/Start-Up_funding_cleaned.csv` — final cleaned file
The last pass, done in Python/pandas (see
[`../data_cleaning/data_cleaning.py`](../data_cleaning/data_cleaning.py) and
the [Data Cleaning README](../data_cleaning/README.md) for the full
walkthrough with screenshots):

1. Dropped the `Remarks` column (~86% empty — no analytical value).
2. Dropped rows with a null / `Undisclosed` / `Unknown` `Amount in USD`.
3. Stripped thousands-separator commas and stray `+` characters from
   `Amount in USD`, then cast it to numeric.
4. Dropped exact duplicate rows and fully empty rows.

**Result:** 3,037 → **2,066 rows**, 10 → **9 columns**. This is the file
loaded into Snowflake as the `STARTUP_FUNDING` table (see
[`../sql/`](../sql/)).
