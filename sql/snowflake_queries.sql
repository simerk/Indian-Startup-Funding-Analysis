/* =====================================================================
   Start-Up Funding – Consumer Internet | Snowflake SQL
   Author: Simerjeet Kaur
   Source: Capstone_project.pptx (Data Manipulation slides)
   =====================================================================
   NOTE: These statements were transcribed from the project's slide
   deck. Re-check column names/types against Start-Up_funding_cleaned.csv
   before running against a fresh Snowflake instance.
   ===================================================================== */

-----------------------------------------------------------------------
-- 1. Create the database / warehouse (adjust names as needed)
-----------------------------------------------------------------------
CREATE OR REPLACE DATABASE CAPSTONE_PROJECT;
CREATE OR REPLACE WAREHOUSE CAPSTONE_WH
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;

USE DATABASE CAPSTONE_PROJECT;
USE SCHEMA PUBLIC;

-----------------------------------------------------------------------
-- 2. Create table STARTUP_FUNDING (loaded from Start-Up_funding_cleaned.csv)
-----------------------------------------------------------------------
CREATE OR REPLACE TABLE "CAPSTONE_PROJECT"."PUBLIC"."STARTUP_FUNDING"
(
    "SR_NO"             INTEGER NOT NULL,
    "DATE"              DATE,
    "STARTUP_NAME"      VARCHAR(1000),
    "INDUSTRY_VERTICAL" VARCHAR(1000),
    "SUB_VERTICAL"      VARCHAR(1000),
    "CITY_LOCATION"     VARCHAR(1000),
    "INVESTORS_NAME"    VARCHAR(1000),
    "INVESTMENT_TYPE"   VARCHAR(1000),
    "AMOUNT_IN_USD"     INTEGER
);

-----------------------------------------------------------------------
-- 3. Total funding in India in each year
--    (excludes rows where the "city" is actually a foreign location
--     picked up from dirty data, e.g. Singapore, San Francisco, etc.)
-----------------------------------------------------------------------
CREATE OR REPLACE TABLE TOTAL_FUNDING_INDIA AS
SELECT
    EXTRACT(YEAR FROM DATE)      AS YEAR,
    SUM(AMOUNT_IN_USD)           AS TOTAL_FUNDINGS_IN_INDIA
FROM STARTUP_FUNDING
WHERE CITY_LOCATION NOT IN (
        'Singapore', 'San Francisco', 'Boston', 'California',
        'Burnsville', 'Menlo Park', 'Nairobi', 'New York',
        'Palo Alto', 'San Jose', 'Santa Monica', 'Tulangan'
      )
GROUP BY YEAR;

-----------------------------------------------------------------------
-- 4. Overall funding in each year (all cities, incl. non-India rows)
-----------------------------------------------------------------------
CREATE OR REPLACE TABLE TOTAL_FUNDING AS
SELECT
    EXTRACT(YEAR FROM DATE) AS YEAR,
    SUM(AMOUNT_IN_USD)      AS TOTAL_FUNDINGS
FROM STARTUP_FUNDING
GROUP BY YEAR;

-----------------------------------------------------------------------
-- 5. Consumer Internet companies funding in each year
-----------------------------------------------------------------------
CREATE OR REPLACE TABLE TOTAL_CONSUMER_INTERNET AS
SELECT
    EXTRACT(YEAR FROM DATE) AS YEAR,
    COUNT(SR_NO)             AS TOTAL_CONSUMER_INTERNET_COMPANIES
FROM STARTUP_FUNDING
WHERE INDUSTRY_VERTICAL = 'Consumer Internet'
GROUP BY YEAR;

-----------------------------------------------------------------------
-- 6. List of funded Consumer Internet companies + funding amount
-----------------------------------------------------------------------
CREATE OR REPLACE TABLE TOTAL_CONSUMER_INTERNET_FUNDING AS
SELECT
    STARTUP_NAME   AS CONSUMER_INTERNET_COMPANIES,
    AMOUNT_IN_USD  AS TOTAL_FUNDINGS
FROM STARTUP_FUNDING
WHERE INDUSTRY_VERTICAL = 'Consumer Internet';

-----------------------------------------------------------------------
-- 7. Companies, by year, that received funding above USD 500,000
-----------------------------------------------------------------------
CREATE OR REPLACE TABLE TOTAL_COMPANIES_ABOVE_500000 AS
SELECT
    EXTRACT(YEAR FROM DATE) AS YEAR,
    COUNT(SR_NO)             AS TOTAL_COMPANIES
FROM STARTUP_FUNDING
WHERE AMOUNT_IN_USD > 500000
GROUP BY YEAR;

-----------------------------------------------------------------------
-- 8. Spread of funded companies across Indian cities
-----------------------------------------------------------------------
CREATE OR REPLACE TABLE COMPANIES_BY_CITY AS
SELECT
    CITY_LOCATION AS CITY,
    COUNT(SR_NO)  AS TOTAL_COMPANIES
FROM STARTUP_FUNDING
GROUP BY CITY_LOCATION
ORDER BY TOTAL_COMPANIES DESC;

-----------------------------------------------------------------------
-- 9. Spread of Consumer Internet companies across cities
-----------------------------------------------------------------------
CREATE OR REPLACE TABLE CONSUMER_INTERNET_BY_CITY AS
SELECT
    CITY_LOCATION AS CITY,
    COUNT(SR_NO)  AS TOTAL_CONSUMER_INTERNET_COMPANIES
FROM STARTUP_FUNDING
WHERE INDUSTRY_VERTICAL = 'Consumer Internet'
GROUP BY CITY_LOCATION
ORDER BY TOTAL_CONSUMER_INTERNET_COMPANIES DESC;

-----------------------------------------------------------------------
-- 10. Companies that received Seed funding, by year
-----------------------------------------------------------------------
CREATE OR REPLACE TABLE SEED_FUNDING_BY_YEAR AS
SELECT
    EXTRACT(YEAR FROM DATE) AS YEAR,
    COUNT(SR_NO)             AS TOTAL_SEED_COMPANIES,
    SUM(AMOUNT_IN_USD)        AS TOTAL_SEED_FUNDING
FROM STARTUP_FUNDING
WHERE INVESTMENT_TYPE ILIKE '%seed%'
GROUP BY YEAR;

-----------------------------------------------------------------------
-- 11. Performance tuning notes
--   - Clustered/queried primarily on DATE and INDUSTRY_VERTICAL, so a
--     clustering key on (INDUSTRY_VERTICAL, DATE) was considered for
--     the base table once it grows beyond a single micro-partition.
--   - Used an XSMALL warehouse with AUTO_SUSPEND to control credit
--     usage for a dataset of this size (~2,000 rows).
--   - Pre-aggregated result tables (TOTAL_FUNDING, TOTAL_FUNDING_INDIA,
--     etc.) instead of having Power BI aggregate on the fly, so the
--     dashboard queries hit small, ready-made summary tables.
-----------------------------------------------------------------------
