# 🚕 Taxi Ride Analytics — End-to-End Data Engineering Project

An end-to-end **Data Engineering learning project** built around a real taxi/ride-booking dataset.

The project starts with a CSV file and progressively turns it into a validated analytical warehouse using **Python, PostgreSQL, SQL, Docker, pytest, logging, and Apache Airflow**.

The main goal is not just to use tools. It is to understand **why each layer exists, what can go wrong, and how a reliable data pipeline is designed**.

---

## 📌 Current Status

The core local data platform is complete.

```text
CSV
 ↓
Python Ingestion
 ↓
RAW
 ↓
STAGING
 ↓
Dimensions + Fact
 ↓
Analytics Views
 ↓
Automated Tests
 ↓
Apache Airflow
```

### Current implementation

| Component | Status |
|---|---|
| Real Kaggle dataset | ✅ |
| Data profiling | ✅ |
| Python ingestion | ✅ |
| PostgreSQL | ✅ |
| Docker | ✅ |
| RAW layer | ✅ |
| STAGING layer | ✅ |
| Dimensional modeling | ✅ |
| Fact table | ✅ |
| Dimension tables | ✅ |
| Analytics views | ✅ |
| Data-quality validation | ✅ |
| Transactions | ✅ |
| Idempotent refresh | ✅ |
| Configuration via `.env` | ✅ |
| Logging | ✅ |
| Automated pytest checks | ✅ |
| Apache Airflow orchestration | ✅ |
| Dashboard | ⏳ |
| dbt | ⏳ |
| Incremental processing | ⏳ |
| Data lake/object storage | ⏳ |
| Spark/PySpark | ⏳ |
| Cloud deployment | ⏳ |
| CI/CD | ⏳ |

---

# 🎯 Project Goals

This project is designed as a practical learning resource for aspiring Data Engineers.

It covers:

- Python for data engineering
- SQL and PostgreSQL
- ETL and ELT
- Data profiling
- Data cleaning
- RAW and STAGING layers
- Data-quality rules
- Star-schema dimensional modeling
- Fact and dimension tables
- Surrogate keys
- Role-playing dimensions
- Transactions
- Idempotency
- Automated testing
- Logging and observability
- Docker
- Apache Airflow
- Future dbt, Spark, cloud, and CI/CD concepts

The project deliberately grows in complexity instead of introducing every data-engineering technology at once.

---

# 🏗️ Current Architecture

```text
                    SOURCE
                      │
                      ▼
             ncr_ride_bookings.csv
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
          ┌───────────┼───────────┐
          ▼           ▼           ▼
    dim_customer  dim_vehicle  dim_location
          │           │           │
          └───────────┼───────────┘
                      ▼
                  fact_rides
                      │
                      ▼
                ANALYTICS VIEWS
                      │
                      ▼
                  Dashboard
                  (planned)


             ┌─────────────────┐
             │ Apache Airflow  │
             │ Orchestration   │
             └────────┬────────┘
                      │
             load_raw
                ↓
        refresh_warehouse
                ↓
             run_tests
```

Airflow is the orchestration layer. It controls **when and in what order** the pipeline tasks execute.

---

# 📊 Dataset

The project uses the **NCR Ride Bookings / Uber Ride Analytics Dashboard** dataset from Kaggle.

Source:

https://www.kaggle.com/datasets/yashdevladdha/uber-ride-analytics-dashboard

Download:

```text
ncr_ride_bookings.csv
```

and place it at:

```text
data/ncr_ride_bookings.csv
```

The source dataset contains:

```text
150,000 rows
21 columns
```

The dataset contains booking information, customers, vehicles, locations, ride metrics, cancellation information, ratings, and payment methods.

---

# 🔎 Initial Data Profiling

Before building the warehouse, the source data was investigated with Python and pandas.

The profiling process checked:

- number of rows
- number of columns
- data types
- missing values
- duplicate rows
- unique identifiers
- categorical distributions
- numeric ranges
- business relationships

### Important discovery

`Booking ID` is **not unique**.

For example, the same booking ID can occur more than once with different source attributes.

Therefore:

```text
Booking ID ≠ row-level primary key
```

The RAW table uses:

```text
raw_id
```

as the unique database-generated lineage identifier.

This is an important data-engineering lesson:

> Never assume that a field is a primary key. Profile the data and verify uniqueness first.

---

# 🧹 Data Quality Findings

The dataset contains many missing values.

Examples include missing:

- booking values
- ride distances
- ratings
- payment methods
- cancellation information
- incomplete-ride information

Missing values are not automatically errors.

For example:

```text
Completed ride
    ↓
booking value expected

Cancelled ride
    ↓
booking value may legitimately be missing
```

Therefore, the project uses **business rules** rather than blindly filling every NULL.

---

# 📈 Booking Status Distribution

| Booking Status | Records |
|---|---:|
| Completed | 93,000 |
| Cancelled by Driver | 27,000 |
| Cancelled by Customer | 10,500 |
| No Driver Found | 10,500 |
| Incomplete | 9,000 |
| **Total** | **150,000** |

Current completion rate:

```text
93,000 / 150,000 = 62%
```

---

# 🚗 Vehicle Distribution

| Vehicle Type | Records |
|---|---:|
| Auto | 37,419 |
| Go Mini | 29,806 |
| Go Sedan | 27,141 |
| Bike | 22,517 |
| Premier Sedan | 18,111 |
| eBike | 10,557 |
| Uber XL | 4,449 |

---

# 🗄️ PostgreSQL

PostgreSQL is used as the local warehouse database.

The database runs inside Docker.

| Setting | Value |
|---|---|
| Database | `taxi_data` |
| User | `data_engineer` |
| Port | `5432` |
| Host from Windows | `localhost` |
| Host from Airflow | `postgres` |

The project uses environment variables for database configuration.

Example `.env`:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=taxi_data
DB_USER=data_engineer
DB_PASSWORD=data_engineering
```

Do **not** commit `.env` to GitHub.

The credentials above are for local learning only.

---

# 🐳 Docker

Docker provides the local PostgreSQL environment without requiring PostgreSQL to be installed directly on Windows.

Start PostgreSQL:

```powershell
docker compose up -d
```

Check containers:

```powershell
docker compose ps
```

Connect to PostgreSQL:

```powershell
docker compose exec postgres psql -U data_engineer -d taxi_data
```

The PostgreSQL data is stored in a Docker named volume, so stopping/removing the container does not automatically remove the database volume.

---

# 🧱 Data Layers

The project follows:

```text
RAW
 ↓
STAGING
 ↓
WAREHOUSE
 ↓
ANALYTICS
```

Each layer has a different responsibility.

## RAW

Preserves what arrived from the source.

Benefits:

- lineage
- recovery
- debugging
- auditing
- reproducibility

Table:

```text
raw_ncr_ride_bookings
```

## STAGING

Converts source data into a cleaner typed representation.

Examples:

```text
TEXT → DATE
TEXT → TIME
TEXT → NUMERIC
"null" → SQL NULL
quoted IDs → cleaned IDs
```

Table:

```text
stg_ncr_ride_bookings
```

## Warehouse

Contains analytical facts and dimensions.

```text
fact_rides
dim_date
dim_customer
dim_vehicle
dim_location
```

## Analytics

Contains reusable business-oriented views.

```text
analytics.booking_summary
analytics.daily_ride_metrics
analytics.vehicle_performance
```

---

# 🧹 Handling the Literal `"null"`

The source contains the text:

```text
null
```

That is different from SQL:

```text
NULL
```

The staging transformation therefore uses logic such as:

```sql
NULLIF(TRIM(booking_value), 'null')::NUMERIC(10, 2)
```

Conceptually:

```text
"null"
   ↓
SQL NULL
   ↓
numeric conversion
```

This prevents invalid casts.

---

# 🧼 Cleaning Source Identifiers

Some identifiers contain surrounding quotes.

Example:

```text
"CNR5292943"
```

The staging layer cleans them using:

```sql
TRIM(BOTH '"' FROM booking_id)
```

RAW keeps the source representation while STAGING provides a cleaner representation.

---

# ⭐ Dimensional Model

The warehouse uses a star schema:

```text
                    dim_date
                       │
                       │
dim_customer ─── fact_rides ─── dim_vehicle
                       │
                       │
                 dim_location
```

## Fact table

```text
fact_rides
```

### Grain

> One row represents one source booking record.

Important columns include:

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

## Dimensions

Current dimensions:

```text
dim_date
dim_customer
dim_vehicle
dim_location
```

---

# 🔑 Surrogate Keys

The warehouse uses generated keys such as:

```text
date_key
customer_key
vehicle_key
location_key
```

These are warehouse identifiers.

They are different from source identifiers:

```text
booking_id
customer_id
```

This separation makes the warehouse model independent of assumptions about source-system identifiers.

---

# 🗺️ Role-Playing Location Dimension

A single location dimension is used for two roles:

```text
                 dim_location
                  /         \
                 /           \
pickup_location_key     drop_location_key
          \                   /
           \                 /
                fact_rides
```

This is called a **role-playing dimension**.

The dimension is the same, but it is used in two different business roles:

```text
Pickup
Drop-off
```

---

# 📅 Date Dimension

The warehouse contains:

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

The dimension covers the full 2024 calendar year, including leap-day, while the source contains 365 unique dates.

---

# 🔄 Warehouse Refresh

The current transformation process uses a full refresh:

```text
RAW
 ↓
Clear STAGING
 ↓
Load STAGING
 ↓
Rebuild dimensions
 ↓
Rebuild FACT
 ↓
Validate
 ↓
COMMIT
```

This is simple and appropriate for the current learning project.

It is also idempotent.

---

# 🔁 Idempotency

A pipeline is idempotent when running it repeatedly produces the same correct state.

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

Later, the project will introduce **incremental loading**, which is more appropriate for continuously growing datasets.

---

# 💾 Transactions

The warehouse refresh is performed inside a PostgreSQL transaction.

Conceptually:

```text
BEGIN
  ↓
Transform
  ↓
Build warehouse
  ↓
Validate
  ↓
COMMIT
```

If something fails:

```text
ERROR
  ↓
ROLLBACK
```

This prevents a partially refreshed warehouse from being committed.

---

# 🧪 Automated Data-Quality Tests

The project uses `pytest` for automated database validation.

The current test suite contains **18 checks** covering areas such as:

- staging/fact row counts
- RAW/staging row counts
- uniqueness
- dimension integrity
- fact foreign keys
- completed-ride business rules
- cancellation business rules
- rating ranges
- allowed booking statuses
- required keys

The tests have been successfully executed through Airflow.

Run locally:

```powershell
python -m pytest
```

Expected result:

```text
18 passed
```

Using:

```powershell
python -m pytest
```

is preferred over calling a separate `pytest` executable because it ensures pytest runs from the same Python environment as the active interpreter.

---

# 📝 Logging

The pipeline includes Python logging.

Logs provide visibility into:

- pipeline start
- database connection
- row counts
- warehouse stages
- validation
- errors
- execution time

Logs are written to:

```text
logs/pipeline.log
```

Generated logs are excluded from Git.

---

# ⚙️ Configuration

Database configuration is separated from pipeline code.

The project uses:

```text
.env
```

and:

```text
src/config.py
```

The application reads environment variables rather than hardcoding database configuration throughout the Python code.

This is a step toward production-ready configuration management.

---

# 🌬️ Apache Airflow

Apache Airflow is now the orchestration layer.

The current DAG is:

```text
taxi_data_pipeline
```

Its tasks are:

```text
load_raw
   ↓
refresh_warehouse
   ↓
run_tests
```

### What Airflow adds

Before Airflow, the pipeline had to be run manually:

```text
python
 ↓
script
 ↓
script
 ↓
pytest
```

With Airflow:

```text
DAG
 ↓
Task dependencies
 ↓
Execution
 ↓
Retries / monitoring
 ↓
Task logs
```

Airflow is responsible for **orchestration**, not for replacing the database or transformation logic.

---

# 🐳 Airflow Docker Setup

The project uses a custom Airflow image.

`airflow/Dockerfile`:

```dockerfile
FROM apache/airflow:3.3.1

USER airflow

RUN pip install --no-cache-dir pytest
```

This ensures the Airflow scheduler has the dependency required to execute:

```powershell
python -m pytest
```

The Airflow stack also includes the components required by Airflow 3, including:

```text
API Server
Scheduler
DAG Processor
```

and a separate PostgreSQL database for Airflow metadata.

---

# 🔐 Airflow JWT Authentication

Airflow components communicate through authenticated APIs.

The local Airflow setup therefore uses a consistent:

```text
AIRFLOW__API_AUTH__JWT_SECRET
```

across the relevant Airflow services.

A mismatch can produce errors such as:

```text
Invalid auth token
```

This was encountered and resolved during the project setup.

For a public repository, the secret should be provided through environment variables rather than committed directly to source control.

---

# ▶️ Running the Pipeline

## 1. Start PostgreSQL

```powershell
docker compose up -d
```

## 2. Load RAW

From the project root:

```powershell
python -m src.load_raw
```

## 3. Refresh warehouse

```powershell
python -m src.refresh_warehouse
```

## 4. Run tests

```powershell
python -m pytest
```

---

# 🌬️ Run with Airflow

Start the Airflow stack:

```powershell
docker compose -f docker-compose.airflow.yml up -d --build
```

If the external Docker network does not exist yet:

```powershell
docker network create taxi-data-engineering_default
```

Then open:

```text
http://localhost:8080
```

Find:

```text
taxi_data_pipeline
```

and trigger it manually.

Expected task flow:

```text
load_raw              🟢
      ↓
refresh_warehouse     🟢
      ↓
run_tests             🟢
```

A successful DAG run means:

```text
CSV ingestion              ✅
Warehouse refresh          ✅
Automated tests            ✅
Airflow orchestration      ✅
```

---

# 📁 Project Structure

```text
taxi-data-engineering/
│
├── data/
│   └── ncr_ride_bookings.csv
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── profile_data.py
│   ├── load_raw.py
│   └── refresh_warehouse.py
│
├── sql/
│   ├── 01_create_raw_table.sql
│   ├── 02_create_staging_table.sql
│   ├── 03_load_staging.sql
│   ├── 04_create_dimensions.sql
│   ├── 05_create_vehicle_dimension.sql
│   ├── 06_create_customer_dimension.sql
│   ├── 07_create_location_dimension.sql
│   ├── 08_create_fact_rides.sql
│   ├── 09_load_fact_rides.sql
│   ├── 10_create_analytics.sql
│   └── 11_vehicle_performance.sql
│
├── tests/
│   └── test_database.py
│
├── airflow/
│   ├── dags/
│   │   └── taxi_pipeline.py
│   ├── logs/
│   └── Dockerfile
│
├── logs/
├── docker-compose.yml
├── docker-compose.airflow.yml
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

Do not commit:

```text
.env
logs/
airflow/logs/
```

The source CSV should also be handled according to the repository's `.gitignore` and Kaggle redistribution terms rather than blindly committing large source data.

---

# 📊 Current Warehouse Results

The current pipeline produces:

```text
RAW records:             150,000
STAGING records:         150,000
FACT records:            150,000

Unique customers:        148,788
Vehicle types:                 7
Locations:                    176
```

---

# 📈 Analytics Layer

The analytics schema contains reusable business views.

## `analytics.booking_summary`

Contains:

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

## `analytics.daily_ride_metrics`

Contains:

```text
full_date
year
month
day_name
total_bookings
completed_rides
completed_revenue
completed_distance
```

## `analytics.vehicle_performance`

Contains:

```text
vehicle_type
completed_rides
completed_revenue
avg_revenue_per_ride
```

---

# 🚗 Vehicle Performance

| Vehicle | Completed Rides | Revenue | Avg Revenue / Ride |
|---|---:|---:|---:|
| Auto | 23,155 | 11,727,615 | 506.48 |
| Go Mini | 18,549 | 9,411,418 | 507.38 |
| Go Sedan | 16,676 | 8,538,560 | 512.03 |
| Bike | 14,034 | 7,144,913 | 509.11 |
| Premier Sedan | 11,252 | 5,733,655 | 509.57 |
| eBike | 6,551 | 3,298,157 | 503.46 |
| Uber XL | 2,783 | 1,406,256 | 505.30 |

The current data suggests that revenue differences are driven substantially by **completed ride volume**, because average revenue per completed ride is relatively similar across vehicle types.

---

# 🧠 Engineering Lessons

This project has already covered several important real-world concepts.

### 1. Profile before designing

Do not design the warehouse based only on column names.

### 2. Do not assume identifiers are unique

`Booking ID` looked like an identifier but was not unique.

### 3. Missing does not mean invalid

Business context matters.

### 4. Preserve RAW

A source-preservation layer makes recovery and debugging easier.

### 5. Define fact-table grain

The grain of `fact_rides` is one source booking record.

### 6. Separate facts and dimensions

Facts store measurements and relationships; dimensions provide context.

### 7. Use surrogate keys carefully

Warehouse keys separate analytical models from source-system identifiers.

### 8. Make pipelines idempotent

A retry should not create duplicate data.

### 9. Use transactions

Validate before committing a warehouse refresh.

### 10. Test business rules

A successful SQL statement does not guarantee correct data.

### 11. Log pipeline behavior

Observability makes failures easier to diagnose.

### 12. Orchestrate after understanding the pipeline

Airflow is much easier to understand once the underlying pipeline already works.

---

# 🗺️ Roadmap

The project will continue toward a more production-like platform.

```text
                         CURRENT
                            │
                            ▼
                    Python + PostgreSQL
                            │
                            ▼
                    Docker + Warehouse
                            │
                            ▼
                  Testing + Logging
                            │
                            ▼
                       Airflow
                            │
                            ▼
                         dbt
                            │
                            ▼
                  Incremental Pipelines
                            │
                            ▼
                Data Lake / Object Storage
                            │
                            ▼
                     Spark / PySpark
                            │
                            ▼
                         Cloud
                            │
                            ▼
                         CI/CD
                            │
                            ▼
                       Dashboard
```

---

# 🚧 Next Phase: dbt

The next major technology is **dbt**.

The architecture will evolve toward:

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

Topics to learn:

- sources
- models
- staging models
- tests
- documentation
- lineage
- macros
- incremental models

The goal is to understand why analytics transformations are often separated from ingestion/orchestration code.

---

# 🔜 Future Phases

## Incremental Processing

Learn:

- watermarks
- upserts
- MERGE
- deduplication
- late-arriving data
- Change Data Capture
- Slowly Changing Dimensions

## Data Lake

Introduce:

- Amazon S3
- Azure Data Lake Storage
- Google Cloud Storage
- Parquet
- partitioning

## Spark

Learn:

- PySpark
- DataFrames
- transformations
- actions
- partitions
- shuffles
- joins
- optimization

## Cloud

Move parts of the local platform to cloud infrastructure.

## CI/CD

Use GitHub Actions for:

```text
Git Push
 ↓
Tests
 ↓
Lint
 ↓
Build
 ↓
Deploy
```

## Dashboard

Connect the analytics layer to:

- Power BI
- Tableau
- Streamlit

Potential KPIs:

- total bookings
- completion rate
- cancellation rate
- revenue
- average revenue per ride
- ride distance
- vehicle performance
- location performance
- daily trends
- cancellation reasons
- ratings

---

# 🧭 Learning Philosophy

Do not learn the project by copying commands.

For every stage, ask:

```text
What problem are we solving?
Why is this layer needed?
Why this table?
What happens if the pipeline fails?
What happens if it runs twice?
How do we know the data is correct?
How would this scale to 1 billion rows?
```

The goal is to move from:

```text
Tool knowledge
```

to:

```text
Engineering understanding
```

---

# 🏁 Final Target Architecture

The eventual platform is planned to look like:

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

                 ┌──────────────────┐
                 │     AIRFLOW      │
                 │   ORCHESTRATION  │
                 └──────────────────┘

                 ┌──────────────────┐
                 │    CI / CD       │
                 │ GitHub Actions   │
                 └──────────────────┘
```

---

# ⭐ Project Philosophy

The objective is not to make the project complicated for the sake of complexity.

The objective is:

```text
Learn
 ↓
Understand
 ↓
Build
 ↓
Validate
 ↓
Automate
 ↓
Scale
```

A strong Data Engineer does not simply know many tools.

A strong Data Engineer understands **why a particular tool, architecture, data model, or reliability mechanism is appropriate for a particular problem**.
