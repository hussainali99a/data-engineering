# Taxi Ride Analytics - End-to-End Data Engineering Project

An end-to-end data engineering project built from a real-world taxi ride booking dataset.

The project currently implements a batch data pipeline:

```text
CSV -> RAW -> STAGING -> FACTS & DIMENSIONS -> ANALYTICS
```

The goal is to build a working pipeline while understanding the engineering decisions behind each stage of a modern data platform. Future phases will introduce orchestration, automated testing, dbt, data lakes, Spark, cloud infrastructure, dashboards, and CI/CD.

## Project Goals

- Learn Python for data engineering
- Learn SQL and PostgreSQL
- Understand ETL and ELT concepts
- Understand data warehousing and dimensional modeling
- Build and use a star schema
- Learn data cleaning and transformation
- Handle missing and invalid values using business rules
- Understand surrogate keys and role-playing dimensions
- Build reusable analytics models
- Implement transactional processing and idempotent refreshes
- Implement data-quality validation
- Containerize PostgreSQL with Docker

## Current Architecture

```text
                         SOURCE
                           |
                           v
                  ncr_ride_bookings.csv
                           |
                           v
                    +-------------+
                    |     RAW     |
                    | PostgreSQL  |
                    +-------------+
                           |
                           v
                    +-------------+
                    |   STAGING   |
                    | Clean / Cast|
                    +-------------+
                           |
              +------------+------------+
              |            |            |
              v            v            v
        dim_customer  dim_vehicle  dim_location
              |            |            |
              +------------+------------+
                           |
                           v
                    +-------------+
                    | fact_rides |
                    +-------------+
                           |
                           v
                    +-------------+
                    |  ANALYTICS  |
                    |    VIEWS    |
                    +-------------+
                           |
                           v
                       Dashboard
```

The dashboard layer is planned but has not yet been implemented.

## Dataset

The project uses the [NCR Ride Bookings dataset](https://www.kaggle.com/datasets/yashdevladdha/uber-ride-analytics-dashboard) from Kaggle.

Download the dataset from Kaggle and place it at:

```text
data/ncr_ride_bookings.csv
```

The dataset is intentionally not committed to this repository. The local `.gitignore` excludes CSV files and generated data.

### Dataset overview

The source dataset contains 150,000 rows and 21 columns covering:

- Ride booking information
- Customer and vehicle information
- Pickup and drop locations
- Ride distance and booking value
- Cancellation and incomplete-ride information
- Driver and customer ratings
- Payment methods

Original columns:

```text
Date
Time
Booking ID
Booking Status
Customer ID
Vehicle Type
Pickup Location
Drop Location
Avg VTAT
Avg CTAT
Cancelled Rides by Customer
Reason for cancellingby Customer
Cancelled Rides by Driver
Driver Cancellation Reason
Incomplete Rides
Incomplete Rides Reason
Booking Value
Ride Distance
Driver Ratings
Customer Rating
Payment Method
```

## Initial Data Profiling

The dataset was profiled with Python and pandas before loading it into PostgreSQL.

- Rows: 150,000
- Columns: 21
- Complete duplicate rows: 0

`Booking ID` is not unique. A booking ID such as `CNR5292943` can appear multiple times with different dates, customers, locations, or statuses. Therefore, `Booking ID` is not used as the primary key. The pipeline preserves `raw_id` as the unique warehouse lineage identifier.

### Important missing-value findings

```text
Avg VTAT                              10,500
Avg CTAT                              48,000
Cancelled Rides by Customer          139,500
Reason for cancelling by Customer    139,500
Cancelled Rides by Driver             123,000
Driver Cancellation Reason            123,000
Incomplete Rides                     141,000
Incomplete Rides Reason              141,000
Booking Value                         48,000
Ride Distance                         48,000
Driver Ratings                        57,000
Customer Rating                       57,000
Payment Method                        48,000
```

Missing data is not automatically bad data. Cancelled rides may legitimately have no booking value, ride distance, payment method, or customer rating. Data quality must be evaluated against business meaning rather than by blindly replacing every NULL.

### Booking status distribution

| Status | Count |
| --- | ---: |
| Completed | 93,000 |
| Cancelled by Driver | 27,000 |
| Cancelled by Customer | 10,500 |
| No Driver Found | 10,500 |
| Incomplete | 9,000 |
| **Total** | **150,000** |

The completion rate is 62%: `93,000 / 150,000`.

### Vehicle types

| Vehicle type | Records |
| --- | ---: |
| Auto | 37,419 |
| Go Mini | 29,806 |
| Go Sedan | 27,141 |
| Bike | 22,517 |
| Premier Sedan | 18,111 |
| eBike | 10,557 |
| Uber XL | 4,449 |

### Payment methods

| Payment method | Count |
| --- | ---: |
| UPI | 45,909 |
| Cash | 25,367 |
| Uber Wallet | 12,276 |
| Credit Card | 10,209 |
| Debit Card | 8,239 |
| Missing / NULL | 48,000 |

The missing payment methods are largely associated with bookings where payment is not applicable.

## PostgreSQL and Docker

PostgreSQL is used as the warehouse database and runs locally in Docker Compose.

| Setting | Value |
| --- | --- |
| Database | `taxi_data` |
| User | `data_engineer` |
| Password | `data_engineering` |
| Port | `5432` |

The current credentials are for local development only. Do not reuse them in production or commit real credentials to GitHub. The next infrastructure phase should move these values to environment variables or secret management.

The current Docker Compose service uses PostgreSQL 17 and a persistent named volume:

```yaml
services:
  postgres:
    image: postgres:17
    environment:
      POSTGRES_USER: data_engineer
      POSTGRES_PASSWORD: data_engineering
      POSTGRES_DB: taxi_data
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

## Project Structure

```text
taxi-data-engineering/
|
|-- data/
|   `-- ncr_ride_bookings.csv          # Download separately from Kaggle
|
|-- src/
|   |-- profile_data.py                # Initial profiling
|   |-- load_raw.py                    # CSV to RAW ingestion
|   `-- refresh_warehouse.py            # STAGING, dimensions, facts, validation
|
|-- sql/
|   |-- 01_create_raw_table.sql
|   |-- 02_create_staging_table.sql
|   |-- 03_load_staging.sql
|   |-- 04_create_dimensions.sql
|   |-- 05_create_vehicle_dimension.sql
|   |-- 06_create_customer_dimension.sql
|   |-- 07_create_location_dimension.sql
|   |-- 08_create_fact_rides.sql
|   |-- 09_load_fact_rides.sql
|   |-- 10_create_analytics.sql
|   `-- 11_vehicle_performance.sql
|
|-- tests/
|-- docker-compose.yml
|-- requirements.txt
|-- .gitignore
`-- README.md
```

## ETL Pipeline

```text
Extract
   |
   v
Load RAW
   |
   v
Transform STAGING
   |
   v
Build dimensions
   |
   v
Build fact table
   |
   v
Validate
   |
   v
Analytics
```

### 1. RAW layer

The RAW table is `raw_ncr_ride_bookings`. It stores source data with minimal transformation, including many fields as `TEXT`:

```text
avg_vtat TEXT
booking_value TEXT
ride_distance TEXT
driver_ratings TEXT
```

RAW represents what arrived from the source rather than what we wish the data looked like. This provides a recovery and audit layer.

The ingestion script uses Python, `psycopg2`, and PostgreSQL `COPY` for bulk loading. Before loading, the current strategy truncates the RAW table:

```sql
TRUNCATE TABLE raw_ncr_ride_bookings;
```

This is a full-refresh strategy and is idempotent for the current dataset.

### 2. STAGING layer

The staging table is `stg_ncr_ride_bookings`. It converts source text into a cleaner, typed representation.

Examples of staging transformations:

- Convert dates, times, and timestamps
- Convert numeric and integer fields
- Convert the literal string `null` to SQL `NULL`
- Remove surrounding quotes from source identifiers
- Standardize values for downstream models

For example:

```sql
NULLIF(TRIM(booking_value), 'null')::NUMERIC(10, 2)
```

The source contains the literal text `null`, which cannot be cast directly to a numeric type. `NULLIF` converts that text into SQL NULL before casting.

Quoted identifiers such as `"CNR5292943"` are cleaned with:

```sql
TRIM(BOTH '"' FROM booking_id)
```

### 3. Data-quality validation

The project validates business rules before and after warehouse construction. Checks include:

- Driver and customer ratings are within the expected range of 3 to 5
- Completed rides contain booking value and ride distance
- Customer cancellations contain customer cancellation reasons
- Driver cancellations contain driver cancellation reasons
- Cancelled and no-driver bookings do not incorrectly contain both booking value and ride distance

## Data Warehouse Model

The warehouse uses a star schema:

```text
                    dim_date
                       |
                       |
dim_customer --- fact_rides --- dim_vehicle
                       |
                       |
                 dim_location
```

### Fact table

The central table is `fact_rides`. Its grain is:

> One row represents one source booking record.

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
cancelled_rides_by_customer
cancelled_rides_by_driver
incomplete_rides
```

### Dimensions and surrogate keys

The warehouse uses surrogate keys for dimensions:

```text
date_key
customer_key
vehicle_key
location_key
```

A fact row stores a warehouse key such as `customer_key = 12345`, while `dim_customer` stores the related source identifier and descriptive attributes.

`dim_location` is used for both pickup and drop locations. The fact table contains `pickup_location_key` and `drop_location_key`, making location a role-playing dimension.

`dim_date` includes `date_key`, `full_date`, `year`, `month`, `day`, `day_of_week`, and `day_name`. It is populated for the full year 2024, including all 366 dates in the leap year. The source dataset contains 365 unique dates, which is expected and acceptable for a complete date dimension.

## Warehouse Results

After a successful refresh, the expected counts are:

```text
STAGING records:       150,000
CUSTOMERS:             148,788
VEHICLES:                    7
LOCATIONS:                  176
FACT rides:            150,000
```

The fact table contains the same number of records as staging.

### Idempotent refresh and transactions

The refresh process is:

```text
RAW
  |
  v
TRUNCATE STAGING
  |
  v
Reload STAGING
  |
  v
Rebuild DIMENSIONS
  |
  v
Rebuild FACT
  |
  v
Validate
  |
  v
COMMIT
```

The transformed tables are cleared before being rebuilt, so repeated runs do not accumulate duplicates. The entire refresh is executed in one PostgreSQL transaction. If any validation or transformation fails, the transaction is rolled back and the partially refreshed warehouse is not committed.

Automated checks currently include:

- STAGING count equals FACT count
- Every fact row has a valid date key
- Every fact row has a valid customer key
- Every fact row has a valid vehicle key
- Every fact row has valid pickup and drop location keys

## Analytics Layer

The `analytics` schema contains reusable SQL views for business analysis and future dashboards.

### `analytics.booking_summary`

Provides total bookings, completed bookings, customer cancellations, driver cancellations, no-driver-found bookings, incomplete bookings, and completion rate. The current completion rate is 62%.

### `analytics.daily_ride_metrics`

Provides daily business metrics including:

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

### `analytics.vehicle_performance`

Provides completed rides, completed revenue, and average revenue per ride by vehicle type.

| Vehicle | Completed rides | Revenue | Average revenue / ride |
| --- | ---: | ---: | ---: |
| Auto | 23,155 | 11,727,615 | 506.48 |
| Go Mini | 18,549 | 9,411,418 | 507.38 |
| Go Sedan | 16,676 | 8,538,560 | 512.03 |
| Bike | 14,034 | 7,144,913 | 509.11 |
| Premier Sedan | 11,252 | 5,733,655 | 509.57 |
| eBike | 6,551 | 3,298,157 | 503.46 |
| Uber XL | 2,783 | 1,406,256 | 505.30 |

Revenue is largely driven by ride volume. Go Sedan has the highest average revenue per completed ride at 512.03, while eBike has the lowest at 503.46. The difference is small compared with the difference in ride volume.

## Technologies Used

| Technology | Purpose |
| --- | --- |
| Python | Data ingestion and pipeline logic |
| pandas | Initial data profiling |
| PostgreSQL | Data warehouse |
| SQL | Transformation and analytics |
| psycopg2 | Python/PostgreSQL connection |
| Docker Compose | Local PostgreSQL infrastructure |

## Running the Project

### Prerequisites

Install the following:

- Python 3
- Docker Desktop with Docker Compose
- Git
- Kaggle dataset downloaded to `data/ncr_ride_bookings.csv`

Create and activate a virtual environment, then install the project dependencies. The current `requirements.txt` is reserved for the Python dependencies used by the project, including `psycopg2` and pandas.

### 1. Start PostgreSQL

From the project root:

```powershell
docker compose up -d
docker compose ps
```

### 2. Create database tables

Connect to PostgreSQL:

```powershell
docker compose exec postgres psql -U data_engineer -d taxi_data
```

Run the SQL files in `sql/` in numeric order, or execute them from your preferred PostgreSQL client. The table creation scripts must run before loading data.

### 3. Profile the data

```powershell
python src/profile_data.py
```

### 4. Load the RAW layer

```powershell
python src/load_raw.py
```

Expected output:

```text
Data loaded successfully.
```

### 5. Refresh the warehouse

```powershell
python src/refresh_warehouse.py
```

Expected output includes:

```text
Clearing transformed tables...
Transformed tables cleared.
Loading STAGING from RAW...
STAGING loaded.
Building vehicle dimension...
Vehicle dimension built.
Building customer dimension...
Customer dimension built.
Building location dimension...
Location dimension built.
Building fact table...
Fact table built.
Running data-quality checks...
All data-quality checks passed.
Warehouse refreshed successfully.
```

### Useful PostgreSQL commands

```sql
\dt
\dn
\d fact_rides
\q
```

## Current Pipeline Status

```text
CSV ingestion                  COMPLETE
RAW layer                      COMPLETE
STAGING layer                  COMPLETE
Data profiling                 COMPLETE
Data quality investigation     COMPLETE
Dimensional model              COMPLETE
Date dimension                 COMPLETE
Customer dimension             COMPLETE
Vehicle dimension              COMPLETE
Location dimension             COMPLETE
Fact table                     COMPLETE
Analytics views                COMPLETE
Full refresh                   COMPLETE
Idempotent refresh             COMPLETE
Transaction handling           COMPLETE
Automated validation           COMPLETE
Dashboard                      PLANNED
```

## Roadmap

### Phase 1 - Foundation

Completed: Python, SQL, PostgreSQL, Docker, ETL/ELT, data modeling, data quality, and analytics.

### Phase 2 - Better testing

- Automated data-quality tests
- Unit tests
- Integration tests
- Business-rule validation
- Pipeline failure testing

### Phase 3 - Logging and observability

- Structured logging
- Pipeline execution logs
- Row-count logging
- Error handling
- Execution metrics

### Phase 4 - Airflow

Introduce DAGs, tasks, operators, scheduling, dependencies, retries, and failure handling.

```text
Airflow -> Extract -> Load RAW -> Transform -> Validate -> Analytics
```

### Phase 5 - dbt

Introduce dbt models, sources, tests, documentation, lineage, incremental models, and macros:

```text
RAW -> STAGING -> dbt models -> FACTS / DIMENSIONS -> ANALYTICS
```

### Phase 6 - Incremental pipelines

Learn incremental loading, watermarks, upserts, MERGE, deduplication, late-arriving data, change data capture, and slowly changing dimensions.

### Phase 7 - Data lake

Evolve the architecture toward object storage such as Amazon S3, Azure Data Lake Storage, or Google Cloud Storage:

```text
Source -> Object Storage / Data Lake -> RAW -> STAGING -> Warehouse
```

### Phase 8 - Apache Spark

Introduce PySpark, DataFrames, transformations, partitions, shuffles, joins, and performance optimization.

### Phase 9 - Cloud

Deploy object storage, a managed database or warehouse, compute, orchestration, and monitoring to a cloud platform.

### Phase 10 - CI/CD

Use GitHub Actions to run tests, linting, builds, and deployment workflows.

### Phase 11 - Dashboard

Expose the analytics layer through Power BI, Tableau, or Streamlit. Potential KPIs include total bookings, completion rate, cancellation rate, revenue, average ride value, ride distance, revenue by vehicle and location, daily booking trends, cancellation reasons, and ratings.

## Final Target Architecture

```text
                         SOURCE
                    CSV / API / Files
                           |
                           v
                    Python Ingestion
                           |
                           v
                    Object Storage
                      / Data Lake
                           |
                           v
                         RAW
                           |
                           v
                       STAGING
                           |
                           v
                         dbt
                           |
                +----------+----------+
                v                     v
           Dimensions               Facts
                |                     |
                +----------+----------+
                           v
                       Analytics
                           |
                           v
                       Dashboard

              Airflow: orchestration layer
              GitHub Actions: CI / CD layer
```

## Learning Philosophy

The project intentionally adds complexity gradually:

```text
Python -> SQL -> PostgreSQL -> Data Modeling -> Docker -> Testing
```

The goal is to understand why each technology exists, not simply how to use it. Airflow, dbt, Spark, cloud services, Kafka, and Kubernetes will be introduced after the underlying pipeline concepts are understood.

## Project Status

**Current status: Core batch data warehouse pipeline completed.**

The project has progressed from a raw CSV to a validated analytical warehouse containing:

- 150,000 source records
- 148,788 unique customers
- 7 vehicle types
- 176 locations
- 150,000 fact records
- A star-schema dimensional model
- Reusable analytics views
- Idempotent full-refresh processing
- Transaction safety
- Automated warehouse validation

The next development phase is advanced testing, logging, and pipeline observability, followed by orchestration with Apache Airflow.
