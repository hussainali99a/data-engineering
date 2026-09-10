# 📚 Data Engineering Learning Guide
## Taxi Ride Analytics — From CSV to an Orchestrated Data Platform

> A beginner-friendly, concept-first learning guide for building an end-to-end Data Engineering project.

This guide explains the **reasoning behind the project**, not just the commands.

The project starts with a real taxi booking CSV and gradually introduces:

```text
Python
 ↓
SQL
 ↓
PostgreSQL
 ↓
ETL / ELT
 ↓
RAW / STAGING
 ↓
Data Modeling
 ↓
Data Quality
 ↓
Testing
 ↓
Logging
 ↓
Docker
 ↓
Airflow
 ↓
dbt
 ↓
Incremental Processing
 ↓
Data Lake
 ↓
Spark
 ↓
Cloud
 ↓
CI/CD
 ↓
Dashboard
```

The first part of this guide represents what has already been built. Later sections represent the learning roadmap.

---

# 1. What Are We Building?

We are building a taxi/ride-booking analytics platform.

The source is:

```text
ncr_ride_bookings.csv
```

The pipeline turns source records into analytical data:

```text
CSV
 ↓
RAW
 ↓
STAGING
 ↓
FACTS + DIMENSIONS
 ↓
ANALYTICS
```

Apache Airflow now orchestrates the process:

```text
load_raw
   ↓
refresh_warehouse
   ↓
run_tests
```

The project is intentionally built in stages so that every new technology solves a problem we have already encountered.

---

# 2. Why Data Engineering?

A business may have data in:

- CSV files
- APIs
- applications
- databases
- event streams
- external systems

But raw data is not automatically useful.

Someone needs to build systems that make data:

- available
- reliable
- organized
- reusable
- trustworthy
- accessible to analysts and applications

That is where Data Engineering comes in.

A simplified platform looks like:

```text
Sources
   ↓
Ingestion
   ↓
Storage
   ↓
Transformation
   ↓
Warehouse
   ↓
Analytics
   ↓
Business Decisions
```

---

# 3. Dataset

The project uses the NCR Ride Bookings dataset from Kaggle:

https://www.kaggle.com/datasets/yashdevladdha/uber-ride-analytics-dashboard

Local file:

```text
data/ncr_ride_bookings.csv
```

Dataset size:

```text
150,000 rows
21 columns
```

The data contains:

- booking information
- customer information
- vehicle types
- pickup/drop locations
- ride metrics
- cancellations
- incomplete rides
- ratings
- payment methods

---

# 4. Data Profiling Comes First

Before creating tables, inspect the data.

Questions to answer:

```text
How many rows?
How many columns?
Which fields are missing?
Which fields are unique?
Which values are categorical?
What are the numeric ranges?
Are there duplicate records?
Do business relationships make sense?
```

The project uses pandas for initial profiling.

This gives us evidence for our data model instead of forcing assumptions onto the source.

---

# 5. Important Discovery: Booking ID Is Not Unique

One of the most valuable discoveries was that:

```text
Booking ID
```

is not unique.

The same booking ID can occur multiple times.

Therefore:

```text
Booking ID ≠ primary key
```

We use:

```text
raw_id
```

as the unique row-level identifier in RAW.

### Why this matters

If we had assumed `booking_id` was unique, we could have:

- created incorrect primary keys
- lost records
- incorrectly deduplicated data
- built incorrect fact-table relationships

### Lesson

> Always test uniqueness. Never infer primary keys from column names.

---

# 6. Missing Data

The dataset has many missing values.

Examples:

```text
Booking Value
Ride Distance
Driver Ratings
Customer Rating
Payment Method
Cancellation information
```

A beginner may think:

```text
NULL = bad data
```

That is not always true.

For example:

```text
Completed ride
    → booking value expected

Cancelled ride
    → booking value may not exist
```

Therefore:

> Data quality must be evaluated using business meaning.

---

# 7. ETL vs ELT

## ETL

```text
Extract
   ↓
Transform
   ↓
Load
```

The transformation happens before loading into the target.

## ELT

```text
Extract
   ↓
Load
   ↓
Transform
```

Raw data reaches the destination first, then transformations happen there.

Our architecture strongly resembles ELT:

```text
CSV
 ↓
RAW
 ↓
STAGING
 ↓
Warehouse
 ↓
Analytics
```

The important lesson is not memorizing the acronym.

The important question is:

> Where should transformation happen, and why?

---

# 8. Why RAW Exists

A common beginner approach is:

```text
CSV
 ↓
Clean everything
 ↓
Warehouse
```

We intentionally avoid that.

Instead:

```text
CSV
 ↓
RAW
 ↓
STAGING
 ↓
Warehouse
```

RAW preserves the source representation.

This helps with:

- debugging
- recovery
- auditing
- lineage
- reproducibility

If a transformation is wrong, we can rebuild downstream layers from RAW.

---

# 9. RAW Table

The table is:

```text
raw_ncr_ride_bookings
```

RAW keeps many fields as text because its job is source preservation rather than analytical perfection.

Examples:

```text
avg_vtat TEXT
booking_value TEXT
ride_distance TEXT
driver_ratings TEXT
```

This gives the transformation layer control over how values are interpreted.

---

# 10. Python Ingestion

Python performs CSV ingestion into PostgreSQL.

The pipeline uses:

```text
Python
psycopg2
PostgreSQL COPY
```

The important concept is bulk loading.

Instead of:

```text
INSERT row 1
INSERT row 2
INSERT row 3
...
INSERT row 150000
```

we use PostgreSQL's bulk-loading mechanism.

Conceptually:

```text
CSV
 ↓
Python
 ↓
COPY
 ↓
RAW
```

This is much closer to how ingestion pipelines should behave than issuing one SQL INSERT per record.

---

# 11. Why `python -m`?

The project contains:

```text
src/
```

and:

```text
src/__init__.py
```

The recommended execution style is:

```powershell
python -m src.load_raw
python -m src.refresh_warehouse
```

rather than:

```powershell
python src/load_raw.py
```

Why?

Because `python -m` executes the file as part of the package structure.

This becomes especially important when code imports:

```python
from src.config import DB_CONFIG
```

---

# 12. STAGING

The staging layer is:

```text
RAW
 ↓
STAGING
```

Its job is to make source data typed and cleaner.

Examples:

```text
TEXT → DATE
TEXT → TIME
TEXT → TIMESTAMP
TEXT → INTEGER
TEXT → NUMERIC
```

It also handles source-specific cleanup.

---

# 13. Literal `"null"` vs SQL `NULL`

The source contains:

```text
"null"
```

as text.

But PostgreSQL understands:

```text
NULL
```

These are not the same.

This would fail:

```sql
'null'::NUMERIC
```

So we use:

```sql
NULLIF(TRIM(field), 'null')::NUMERIC
```

Conceptually:

```text
"null"
  ↓
NULLIF
  ↓
SQL NULL
  ↓
NUMERIC conversion
```

This is a very common ingestion problem.

---

# 14. Cleaning Quoted IDs

Source identifiers may look like:

```text
"CNR5292943"
```

The staging layer removes the surrounding quotes:

```sql
TRIM(BOTH '"' FROM booking_id)
```

This illustrates an important pattern:

```text
RAW
    = preserve source

STAGING
    = standardize source
```

---

# 15. Data Warehouse Modeling

A cleaned table is not automatically a good analytical model.

Analytics often benefits from dimensional modeling.

Our warehouse uses a:

# ⭐ Star Schema

```text
                    dim_date
                       │
                       │
dim_customer ─── fact_rides ─── dim_vehicle
                       │
                       │
                 dim_location
```

The center is the fact table.

The surrounding tables are dimensions.

---

# 16. Fact Table Grain

The fact table is:

```text
fact_rides
```

Before designing a fact table, define its **grain**.

Our grain is:

> One row in `fact_rides` represents one source booking record.

This is one of the most important decisions in dimensional modeling.

If the grain is unclear, measures can be double-counted or relationships can become ambiguous.

---

# 17. Fact Table

The fact table stores measures and relationships.

Important fields include:

```text
ride_key
raw_id
booking_id
date_key
customer_key
vehicle_key
pickup_location_key
drop_location_key
booking_status
booking_value
ride_distance
avg_vtat
avg_ctat
driver_rating
customer_rating
```

The fact table also contains cancellation/incomplete ride indicators.

---

# 18. Dimension Tables

Current dimensions:

```text
dim_date
dim_customer
dim_vehicle
dim_location
```

A dimension stores descriptive context.

For example:

```text
fact_rides.vehicle_key
        ↓
dim_vehicle
        ↓
vehicle_type = Go Sedan
```

The fact says:

> Which vehicle?

The dimension says:

> What is that vehicle?

---

# 19. Surrogate Keys

Warehouse dimensions use generated keys:

```text
date_key
customer_key
vehicle_key
location_key
```

These are called surrogate keys.

They are different from source identifiers:

```text
customer_id
booking_id
```

Why separate them?

Because source identifiers can have:

- duplicates
- format changes
- inconsistent systems
- business-specific semantics

The warehouse should not depend blindly on source-system assumptions.

---

# 20. Date Dimension

The project contains:

```text
dim_date
```

with:

```text
date_key
full_date
year
month
day
day_of_week
day_name
```

A date dimension makes time analysis easier.

Instead of repeatedly deriving:

```text
year
month
day
weekday
```

from timestamps, the warehouse provides those attributes directly.

---

# 21. Role-Playing Dimension

`dim_location` is used twice.

```text
                 dim_location
                  /         \
                 /           \
pickup_location_key     drop_location_key
          \                   /
           \                 /
                fact_rides
```

The same dimension plays two roles:

```text
Pickup Location
Drop Location
```

This is a **role-playing dimension**.

---

# 22. Data Quality

Data quality is more than:

```text
SQL query succeeded
```

A pipeline can execute successfully and still produce incorrect data.

The project therefore checks business rules.

Examples:

```text
Completed ride
→ booking value should exist

Completed ride
→ ride distance should exist

Customer cancellation
→ customer cancellation reason should exist

Driver cancellation
→ driver cancellation reason should exist

Ratings
→ expected range
```

---

# 23. Referential Integrity

Fact rows reference dimensions.

For example:

```text
fact_rides.customer_key
        ↓
dim_customer.customer_key
```

We check that every fact key resolves to a valid dimension record.

The same principle applies to:

```text
date
vehicle
pickup location
drop location
```

A broken reference means the warehouse contains an integrity problem.

---

# 24. Transactions

Warehouse refresh is transactional.

Conceptually:

```text
BEGIN
 ↓
Clear transformed layers
 ↓
Load staging
 ↓
Build dimensions
 ↓
Build fact
 ↓
Validate
 ↓
COMMIT
```

If anything fails:

```text
ERROR
 ↓
ROLLBACK
```

Why?

Because we don't want:

```text
STAGING = new data
FACT = half old / half new
```

Transactions protect consistency.

---

# 25. Idempotency

A pipeline should be safe to retry.

Without idempotency:

```text
Run 1 → 150,000
Run 2 → 300,000
Run 3 → 450,000
```

With the current full-refresh design:

```text
Run 1 → 150,000
Run 2 → 150,000
Run 3 → 150,000
```

This is idempotency.

---

# 26. Full Refresh

The current transformed layers use a full refresh:

```text
RAW
 ↓
TRUNCATE STAGING
 ↓
Reload STAGING
 ↓
Rebuild dimensions
 ↓
Rebuild fact
 ↓
Validate
 ↓
Commit
```

This is simple and appropriate for our current learning dataset.

It is not the final strategy for a large continuously changing production system.

Later we will learn incremental pipelines.

---

# 27. Configuration and Secrets

The database configuration is separated from the code.

The project uses:

```text
.env
```

and:

```text
src/config.py
```

Example:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=taxi_data
DB_USER=data_engineer
DB_PASSWORD=data_engineering
```

The `.env` file must not be committed to GitHub.

This introduces the concept of:

```text
Application code
       +
Environment configuration
```

instead of:

```text
Application code
       +
Hardcoded secrets
```

---

# 28. Logging

The pipeline now uses Python logging.

Useful events include:

```text
Pipeline started
Database connected
RAW loaded
STAGING loaded
Dimension counts
FACT loaded
Validation passed
Pipeline completed
Execution time
```

Logs are written to:

```text
logs/pipeline.log
```

Logging is more useful than relying only on `print()` because it gives us:

- severity levels
- structured messages
- persistent logs
- easier debugging

---

# 29. Automated Testing

The project uses `pytest`.

The current suite contains:

```text
18 tests
```

The tests validate:

- row counts
- uniqueness
- foreign keys
- rating ranges
- booking statuses
- completed-ride rules
- cancellation rules
- required keys

Run:

```powershell
python -m pytest
```

Expected:

```text
18 passed
```

The important concept is:

```text
Pipeline
   ↓
Validation
   ↓
Trust
```

---

# 30. Why Test the Database?

These are not only unit tests for Python functions.

They are also **database/data-quality tests**.

For example:

```text
Does every fact row have a valid customer?
```

That question cannot be answered by testing only whether a Python function runs.

It requires checking the actual warehouse state.

---

# 31. Docker

Docker gives the project a reproducible local infrastructure environment.

Without Docker:

```text
Install PostgreSQL manually
Configure PostgreSQL
Create users
Create database
```

With Docker:

```text
docker compose up -d
```

and PostgreSQL starts as a container.

The project uses a named volume for PostgreSQL data persistence.

---

# 32. Airflow: Why Do We Need It?

Before Airflow, we manually executed:

```text
load_raw
 ↓
refresh_warehouse
 ↓
pytest
```

But production pipelines need orchestration.

Questions arise:

```text
When should the pipeline run?
What happens if task 1 fails?
Should task 2 run?
Should a failed task retry?
Where do we inspect logs?
What is the status of today's run?
```

Airflow answers these orchestration questions.

---

# 33. Airflow DAG

Our DAG is:

```text
taxi_data_pipeline
```

The task dependency is:

```text
load_raw
   ↓
refresh_warehouse
   ↓
run_tests
```

This means:

```text
refresh_warehouse
```

does not start until:

```text
load_raw
```

succeeds.

And:

```text
run_tests
```

does not start until:

```text
refresh_warehouse
```

succeeds.

---

# 34. Airflow Components

The local Airflow 3 setup uses components including:

```text
API Server
Scheduler
DAG Processor
```

A separate PostgreSQL database stores Airflow metadata.

The project also mounts the project into the Airflow containers so that the DAG can execute:

```text
/opt/airflow/project
```

---

# 35. Airflow and the Project Database

There are two different PostgreSQL purposes.

### Airflow PostgreSQL

Stores:

```text
Airflow metadata
DAG state
Task state
Runs
```

### Taxi PostgreSQL

Stores:

```text
RAW
STAGING
FACTS
DIMENSIONS
ANALYTICS
```

Conceptually:

```text
Airflow
   │
   ├── Airflow metadata DB
   │
   └── orchestrates
            │
            ▼
      Taxi warehouse DB
```

Keeping these responsibilities separate is useful.

---

# 36. Airflow Docker Dependencies

Airflow runs in its own Docker environment.

Therefore:

```text
pytest installed on Windows
```

does not mean:

```text
pytest installed inside Airflow
```

We solved this by building a custom Airflow image.

```dockerfile
FROM apache/airflow:3.3.1

USER airflow

RUN pip install --no-cache-dir pytest
```

The important lesson is:

> Container dependencies belong to the container image.

---

# 37. Airflow JWT Authentication

Airflow 3 components communicate through APIs.

The local stack requires a consistent:

```text
AIRFLOW__API_AUTH__JWT_SECRET
```

across the relevant components.

If components use different values, API calls can fail with:

```text
Invalid auth token
```

This was an important debugging lesson because the DAG appeared correctly in the UI but task execution initially failed.

---

# 38. Airflow Result

The completed DAG run now looks like:

```text
load_raw              🟢
      ↓
refresh_warehouse     🟢
      ↓
run_tests             🟢
```

The complete DAG run is:

```text
SUCCESS
```

This means the pipeline is now:

```text
Ingested
   ↓
Transformed
   ↓
Validated
   ↓
Orchestrated
```

---

# 39. Current Architecture

At this stage:

```text
                  CSV
                   │
                   ▼
            Python Ingestion
                   │
                   ▼
                  RAW
                   │
                   ▼
               STAGING
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
        Date   Customer  Vehicle
          │        │        │
          └────────┼────────┘
                   ▼
              fact_rides
                   │
                   ▼
               Analytics
                   │
                   ▼
                Reports


              AIRFLOW
                 │
                 ▼
       ┌──────────────────┐
       │   load_raw       │
       │        ↓         │
       │ refresh_warehouse│
       │        ↓         │
       │    run_tests     │
       └──────────────────┘
```

---

# 40. Analytics Layer

The analytics schema contains reusable views.

## Booking Summary

```text
analytics.booking_summary
```

Provides:

```text
total_bookings
completed_bookings
customer_cancellations
driver_cancellations
no_driver_found
incomplete_bookings
completion_rate_pct
```

Current completion rate:

```text
62%
```

## Daily Metrics

```text
analytics.daily_ride_metrics
```

Provides:

```text
date
year
month
day
total_bookings
completed_rides
completed_revenue
completed_distance
```

## Vehicle Performance

```text
analytics.vehicle_performance
```

Provides:

```text
vehicle_type
completed_rides
completed_revenue
avg_revenue_per_ride
```

---

# 41. Current Warehouse State

The current successful pipeline produces:

```text
RAW                  150,000
STAGING              150,000
FACT                 150,000

CUSTOMERS            148,788
VEHICLE TYPES              7
LOCATIONS                 176
```

This gives us a stable baseline for future improvements.

---

# 42. What We Have Learned

At this point, the project has covered:

```text
Python
SQL
PostgreSQL
Docker
ETL / ELT
Data profiling
Data cleaning
RAW layer
STAGING layer
Data modeling
Star schema
Fact tables
Dimension tables
Surrogate keys
Role-playing dimensions
Data quality
Transactions
Idempotency
Configuration
Logging
Automated tests
Airflow
Dockerized Airflow
```

The important thing is not the list.

The important thing is that each concept was introduced because the project needed it.

---

# 43. What Comes Next?

The next major phase is:

# dbt

Why dbt?

Our transformation logic currently lives largely in:

```text
Python
+
SQL
```

As analytical transformations grow, we want a structured transformation framework.

dbt will help us learn:

```text
Sources
Models
Tests
Documentation
Lineage
Macros
Incremental Models
```

The architecture becomes:

```text
RAW
 ↓
STAGING
 ↓
dbt
 ↓
FACTS + DIMENSIONS
 ↓
ANALYTICS
```

---

# 44. Incremental Pipelines

Our current strategy is:

```text
Full Refresh
```

Later we need to handle:

```text
New data arrives
       ↓
Process only new/changed records
```

Topics:

- watermarks
- incremental loads
- upserts
- MERGE
- deduplication
- late-arriving data
- Change Data Capture
- Slowly Changing Dimensions

This is where the project begins moving from a simple batch exercise toward production-style pipelines.

---

# 45. Data Lake

Next, storage can evolve from:

```text
CSV → PostgreSQL
```

toward:

```text
Source
 ↓
Object Storage
 ↓
RAW
 ↓
STAGING
 ↓
Warehouse
```

Possible technologies:

```text
Amazon S3
Azure Data Lake Storage
Google Cloud Storage
```

We will also learn formats such as:

```text
Parquet
```

and concepts such as:

```text
partitioning
file layout
schema evolution
```

---

# 46. Apache Spark

When data becomes too large for simple single-machine processing, Spark becomes useful.

Topics:

```text
PySpark
DataFrames
Transformations
Actions
Partitions
Shuffles
Joins
Caching
Performance
```

The important question will be:

> When is Spark actually needed?

We should not introduce Spark just because it is popular.

---

# 47. Cloud

The local architecture can eventually become:

```text
Local Docker
```

→

```text
Cloud Storage
+
Managed Database/Warehouse
+
Compute
+
Orchestration
+
Monitoring
```

Possible cloud platforms:

```text
AWS
Azure
GCP
```

The project can then become a real cloud portfolio project.

---

# 48. CI/CD

GitHub Actions can automate:

```text
Git Push
 ↓
Install dependencies
 ↓
Run tests
 ↓
Lint
 ↓
Build
 ↓
Deploy
```

This introduces software-engineering practices into the data pipeline.

---

# 49. Dashboard

The analytics layer will eventually feed a dashboard.

Potential KPIs:

```text
Total Bookings
Completion Rate
Cancellation Rate
Revenue
Average Revenue / Ride
Ride Distance
Vehicle Performance
Location Performance
Daily Trends
Cancellation Reasons
Driver Ratings
Customer Ratings
```

Possible tools:

```text
Power BI
Tableau
Streamlit
```

---

# 50. Final Target Architecture

The eventual project is planned to become:

```text
                         SOURCE
                    CSV / API / Files
                           │
                           ▼
                    Python Ingestion
                           │
                           ▼
                    Object Storage
                       / Data Lake
                           │
                           ▼
                          RAW
                           │
                           ▼
                       STAGING
                           │
                           ▼
                          dbt
                           │
                ┌──────────┴──────────┐
                ▼                     ▼
           DIMENSIONS               FACTS
                │                     │
                └──────────┬──────────┘
                           ▼
                       ANALYTICS
                           │
                           ▼
                       DASHBOARD

                  ┌─────────────────┐
                  │     AIRFLOW     │
                  │  ORCHESTRATION  │
                  └─────────────────┘

                  ┌─────────────────┐
                  │    CI / CD      │
                  │ GitHub Actions  │
                  └─────────────────┘
```

---

# 51. Beginner Learning Checklist

Use this checklist while working through the project.

## Python

- [x] Modules
- [x] Packages
- [x] Environment variables
- [x] PostgreSQL connections
- [x] Logging
- [x] Exceptions
- [x] Execution timing

## SQL

- [x] CREATE TABLE
- [x] INSERT / SELECT
- [x] JOIN
- [x] GROUP BY
- [x] CASE
- [x] NULL handling
- [x] FILTER
- [x] Views
- [x] Foreign keys
- [x] Transactions

## Data Engineering

- [x] ETL
- [x] ELT
- [x] RAW layer
- [x] STAGING
- [x] Data quality
- [x] Idempotency
- [x] Data modeling
- [x] Fact tables
- [x] Dimensions
- [x] Grain
- [x] Surrogate keys
- [x] Role-playing dimensions

## Infrastructure

- [x] Docker
- [x] Docker Compose
- [x] Docker networking
- [x] Persistent volumes
- [x] Container-specific dependencies

## Reliability

- [x] Transactions
- [x] Validation
- [x] Automated tests
- [x] Logging
- [x] Failure investigation

## Orchestration

- [x] DAG
- [x] Tasks
- [x] Dependencies
- [x] Airflow scheduler
- [x] DAG processor
- [x] API server
- [x] Task logs
- [x] Dockerized Airflow

## Future

- [ ] dbt
- [ ] Incremental models
- [ ] Data lake
- [ ] Parquet
- [ ] Spark
- [ ] Cloud
- [ ] CI/CD
- [ ] Dashboard

---

# 52. Questions To Ask at Every Stage

The most important habit is to ask:

### What problem are we solving?

### Why do we need this layer?

### Why this technology?

### What happens if the task fails?

### What happens if the pipeline runs twice?

### How do we know the data is correct?

### What happens when the data becomes 100x larger?

### What happens if the source schema changes?

### How would this work in the cloud?

These questions develop engineering thinking.

---

# 53. Final Learning Philosophy

Do not aim to memorize:

```text
Airflow commands
SQL commands
Docker commands
Spark commands
```

Instead, aim to understand:

```text
Problem
 ↓
Architecture
 ↓
Implementation
 ↓
Validation
 ↓
Automation
 ↓
Scale
```

The project follows:

```text
Learn
 ↓
Understand
 ↓
Build
 ↓
Break
 ↓
Debug
 ↓
Validate
 ↓
Automate
 ↓
Scale
```

The debugging experiences are part of the learning.

For example, the Airflow phase exposed:

```text
DAG parsing
Docker networking
container dependencies
Windows vs Linux paths
JWT authentication
task execution
pytest environment
```

Those problems are valuable because they teach how the individual components behave in a real system.

---

# 🏁 Current Milestone

The project has successfully reached:

```text
                    ┌───────────────┐
                    │      CSV      │
                    └───────┬───────┘
                            ↓
                    ┌───────────────┐
                    │    Python     │
                    │   Ingestion   │
                    └───────┬───────┘
                            ↓
                    ┌───────────────┐
                    │      RAW      │
                    └───────┬───────┘
                            ↓
                    ┌───────────────┐
                    │   STAGING     │
                    └───────┬───────┘
                            ↓
                 ┌──────────┴──────────┐
                 ↓                     ↓
            DIMENSIONS               FACT
                 └──────────┬──────────┘
                            ↓
                       ANALYTICS
                            ↓
                         TESTS
                            ↓
                        AIRFLOW
                            ↓
                         SUCCESS
```

This is a strong foundation.

The next step is not to add random technologies.

The next step is to make the **transformation layer more professional with dbt**, then introduce incremental processing, data-lake concepts, Spark, cloud, CI/CD, and finally a dashboard.

---

## ⭐ Core Principle

> **Don't build the most complicated pipeline. Build the pipeline you can explain.**

If you can explain:

```text
Why RAW exists
Why STAGING exists
Why Booking ID is not the primary key
Why the fact grain matters
Why dimensions exist
Why surrogate keys exist
Why transactions are needed
Why idempotency matters
Why tests are required
Why Airflow is useful
```

then you are learning Data Engineering rather than simply collecting tools.
