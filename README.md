# Indian Startup Funding Analysis

Python + Snowflake + Power BI pipeline analyzing Indian startup funding
trends (2015–19), with a focus on the Consumer Internet sector, built for an
international investor.

**Author:** Simerjeet Kaur

---

## Project Brief

> *"I am an international investor looking at data of funded companies from
> India between 2015–19. I am particularly interested in Consumer
> Internet."*

The brief asked for a database and dashboard answering: total funding in
India per year, overall funding per year, Consumer Internet funding per
year, a list of funded Consumer Internet companies, the spread of funded
companies (all and Consumer Internet) across Indian cities, how many
companies received Seed funding each year, and which companies were funded
above USD 500,000. Full brief: [`docs/My_Questions.docx`](docs/My_Questions.docx).

## Pipeline & Tech Stack

```
Raw CSV export  ──►  Python cleaning  ──►  Snowflake (SQL)  ──►  Power BI dashboard
   (broken,          (pandas: parse,       (tables, summary        (2 pages, KPIs,
    single-blob        declutter, fix        aggregations,          map, trend charts)
    rows)              types, dedupe)        performance tuning)
```

| Stage | Tool | Folder |
|---|---|---|
| Data | Raw → cleaned CSVs at every stage | [`data/`](data/) |
| Cleaning | Python / pandas | [`data_cleaning/`](data_cleaning/) |
| Manipulation | Snowflake SQL | [`sql/`](sql/) |
| Visualization | Power BI | [`dashboard/`](dashboard/) |
| Reference docs | Original brief + walkthrough deck | [`docs/`](docs/) |

Each folder above has its own README with the full detail for that stage —
this file is just the overview.

## Repository Structure

```
.
├── README.md                    <- you are here
├── data/
│   ├── README.md                 <- what each raw/cleaned file is, and what changed
│   ├── raw/
│   │   ├── Start-up_Funding1.csv       # raw export, as given
│   │   ├── Start-up_Funding2.csv       # columns split
│   │   └── Start-Up_Funding.csv        # unwanted characters removed
│   └── processed/
│       └── Start-Up_funding_cleaned.csv  # final, analysis-ready file
├── data_cleaning/
│   ├── README.md                 <- cleaning pipeline walkthrough + screenshots
│   └── data_cleaning.py          # reproduces raw -> cleaned end to end
├── sql/
│   ├── README.md                 <- Snowflake tables + performance tuning notes
│   └── snowflake_queries.sql
├── dashboard/
│   ├── README.md                 <- dashboard pages + screenshots
│   ├── Capstone_project.pbix
│   └── screenshots/
└── docs/
    ├── My_Questions.docx         # original brief
    └── Capstone_project.pptx     # project walkthrough deck
```

## Key Insights

- Indian startup funding peaked in **2017** (~$10.4bn across 456 deals) and
  fell sharply through 2018–19; 2019's total stayed respectable (~$9.7bn)
  thanks to a few large late-stage deals, despite far fewer deals overall (105).
- **Bangalore, Mumbai, and Delhi-NCR (New Delhi + Gurugram)** dominate the
  funding map, together hosting the large majority of funded companies.
- Seed-stage activity contracted the most — from 300 seed deals in 2015 to a
  handful by 2018–19 — suggesting the ecosystem matured toward larger,
  later-stage rounds.
- Consumer Internet remained active but was not the top vertical by deal
  count relative to E-Commerce and Technology.

## How to Reproduce

1. **Clean the data:** `python data_cleaning/data_cleaning.py` (see
   [`data_cleaning/README.md`](data_cleaning/README.md)).
2. **Load into Snowflake:** run [`sql/snowflake_queries.sql`](sql/snowflake_queries.sql)
   against the cleaned CSV (see [`sql/README.md`](sql/README.md)).
3. **Open the dashboard:** `dashboard/Capstone_project.pbix` in Power BI
   Desktop, pointed at your Snowflake instance (see
   [`dashboard/README.md`](dashboard/README.md)).
