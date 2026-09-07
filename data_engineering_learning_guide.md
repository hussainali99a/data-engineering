# 📚 Data Engineering Learning Journey — Taxi Ride Analytics

> A practical, beginner-friendly, end-to-end data engineering project designed to teach **concepts, decisions, and engineering practices** — not just code.

---

## 🎯 Why This Repository Exists

This repository is being built as a **learning resource for aspiring data engineers**.

The idea is simple:

> Don't just learn data engineering tools individually. Learn how the pieces fit together by building a real pipeline from raw data to analytics.

A person starting from beginner level should be able to follow this repository and understand:

- What data engineering is
- Why data pipelines exist
- How raw data becomes useful analytical data
- Why databases and warehouses are structured differently
- What ETL and ELT mean
- How to design fact and dimension tables
- How to handle dirty data
- How to validate data
- What idempotency means
- Why transactions matter
- How orchestration tools such as Airflow fit into a pipeline
- Why dbt, Spark, cloud storage, and CI/CD are used in larger systems

The project will grow gradually from a simple local pipeline into a more production-like data platform.

---

# 🗺️ Learning Roadmap

The project follows this progression:

```text
1. Python + SQL + PostgreSQL
            ↓
2. ETL / ELT concepts
            ↓
3. Raw and Staging layers
            ↓
4. Data Quality
            ↓
5. Dimensional Modeling
            ↓
6. Fact & Dimension Tables
            ↓
7. Analytics Layer
            ↓
8. Idempotency & Transactions
            ↓
9. Automated Testing
            ↓
10. Logging & Observability
            ↓
11. Apache Airflow
            ↓
12. dbt
            ↓
13. Incremental Pipelines
            ↓
14. Data Lake / Object Storage
            ↓
15. Apache Spark / PySpark
            ↓
16. Cloud
            ↓
17. CI/CD
            ↓
18. Dashboard
```

The project is intentionally incremental.

We do **not** start by throwing Airflow, Spark, Kafka, Kubernetes, AWS, and ten other technologies at a beginner.

We first understand the fundamentals.

---

# 🚕 Project: Taxi Ride Analytics

Our example business is a taxi/ride-booking platform.

We want to answer questions such as:

- How many rides were completed?
- What is the completion rate?
- How many rides were cancelled?
- Which vehicle types generate the most revenue?
- What is the average revenue per ride?
- Which locations are most active?
- How does ride activity change over time?
- What are the major cancellation reasons?
- How do customer and driver ratings look?

To answer these questions reliably, we need to build a data pipeline.

---

# 📊 Dataset

The project uses a real taxi ride dataset from Kaggle:

**NCR Ride Bookings / Uber Ride Analytics Dashboard**

Source:

https://www.kaggle.com/datasets/yashdevladdha/uber-ride-analytics-dashboard

The local file is:

```text
data/ncr_ride_bookings.csv
```

Dataset size:

```text
150,000 rows
21 columns
```

---

# 🧠 Chapter 1 — What Is Data Engineering?

Data engineering is largely about building systems that make data:

- available
- reliable
- organized
- trustworthy
- reusable
- accessible for analytics and downstream applications

A simplified picture is:

```text
Data Sources
     ↓
Ingestion
     ↓
Storage
     ↓
Transformation
     ↓
Data Warehouse
     ↓
Analytics
     ↓
Business Decisions
```

A data engineer builds and maintains the systems connecting these stages.

---

# 🧠 Chapter 2 — ETL vs ELT

## ETL

ETL means:

```text
Extract → Transform → Load
```

Data is transformed before it reaches the destination.

## ELT

ELT means:

```text
Extract → Load → Transform
```

The raw data is loaded first and transformations happen inside the destination system.

Our project follows a pattern that strongly resembles ELT:

```text
CSV
 ↓
RAW
 ↓
STAGING
 ↓
Warehouse Models
 ↓
Analytics
```

The important lesson is not memorizing the acronym.

The important lesson is understanding **where transformation happens and why**.

---

# 🧠 Chapter 3 — Why Do We Need a RAW Layer?

A common beginner question is:

> Why not just clean the CSV and put the cleaned data into PostgreSQL?

Because the original data is valuable.

The RAW layer acts as a source-preservation layer.

```text
Source
  ↓
RAW
  ↓
Transformations
```

If a transformation introduces a bug, we can go back to RAW and rebuild.

RAW also provides:

- lineage
- auditing
- reproducibility
- debugging
- recovery

Our RAW table is:

```text
raw_ncr_ride_bookings
```

---

# 🐍 Chapter 4 — Python Ingestion

Python is used to load the CSV into PostgreSQL.

The important libraries currently include:

```text
Python
psycopg2
```

For bulk loading, PostgreSQL's `COPY` mechanism is used.

Instead of doing:

```text
INSERT row 1
INSERT row 2
INSERT row 3
...
INSERT row 150000
```

we use a bulk-loading operation.

Conceptually:

```text
CSV
 ↓
Python
 ↓
PostgreSQL COPY
 ↓
RAW
```

This is an important practical data-engineering pattern.

---

# 🧠 Chapter 5 — Data Profiling

Before transforming data, we inspected it.

Using pandas, we checked:

- row count
- column count
- data types
- missing values
- duplicates
- unique values
- distributions
- ranges
- business relationships

This is a critical habit.

> **Understand the data before designing the pipeline.**

---

# 🔎 Important Dataset Discovery: Booking ID Is Not Unique

One of the most important discoveries was that `Booking ID` cannot be treated as a primary key.

The same booking ID can appear multiple times with different:

- dates
- customers
- locations
- statuses

Therefore:

```text
Booking ID ≠ unique row identifier
```

We preserved a database-generated:

```text
raw_id
```

which uniquely identifies each source row.

This teaches an important lesson:

> Never assume a column is unique simply because its name sounds like an identifier.

Always investigate the data.

---

# 🧹 Chapter 6 — Missing Data

The dataset contains many missing values.

For example:

- booking value
- ride distance
- payment method
- ratings
- cancellation information

At first this might look like bad data.

But context matters.

For example:

```text
Completed ride
    → booking value expected

Cancelled ride
    → booking value may not exist
```

Therefore:

> Missing does not automatically mean invalid.

Data quality requires understanding the business rules.

---

# 🧠 Chapter 7 — Literal `"null"` vs SQL NULL

The source contains the text:

```text
null
```

That is different from PostgreSQL's:

```text
NULL
```

This caused an important transformation problem.

For example:

```sql
'null'::NUMERIC
```

fails.

We therefore use:

```sql
NULLIF(TRIM(field), 'null')::NUMERIC
```

Conceptually:

```text
"null"
  ↓
SQL NULL
  ↓
numeric conversion
```

This is a common real-world ingestion problem.

---

# 🧹 Chapter 8 — Cleaning Identifiers

The source contains identifiers with surrounding quotes.

For example:

```text
"CNR5292943"
```

The staging layer converts this into:

```text
CNR5292943
```

using:

```sql
TRIM(BOTH '"' FROM booking_id)
```

Again, RAW preserves the source representation while STAGING provides a cleaner representation.

---

# 🏗️ Chapter 9 — STAGING

The staging layer sits between RAW and the warehouse.

```text
RAW
 ↓
STAGING
 ↓
Warehouse
```

RAW preserves the source.

STAGING makes the data usable.

Examples of staging transformations:

```text
TEXT → DATE
TEXT → TIME
TEXT → TIMESTAMP
TEXT → INTEGER
TEXT → NUMERIC
"null" → NULL
quoted ID → clean ID
```

Our staging table is:

```text
stg_ncr_ride_bookings
```

---

# 🧠 Chapter 10 — Why Create a Data Warehouse Model?

A cleaned table is not necessarily a good analytical model.

For analytics, we want data that is:

- easy to query
- consistent
- reusable
- understandable
- efficient for reporting

This is where dimensional modeling comes in.

Our warehouse uses a **star schema**.

---

# ⭐ Chapter 11 — Star Schema

Our architecture is:

```text
                    dim_date
                       │
                       │
dim_customer ─── fact_rides ─── dim_vehicle
                       │
                       │
                 dim_location
```

The central table is the fact table.

The surrounding tables are dimensions.

---

# 📦 Chapter 12 — Fact Tables

Our fact table is:

```text
fact_rides
```

The most important concept is the **grain**.

Our grain is:

> One row in `fact_rides` represents one source booking record.

This decision should be made before designing the fact table.

The fact table contains:

- foreign keys
- measurements
- status
- business metrics

Examples:

```text
booking_value
ride_distance
avg_vtat
avg_ctat
driver_rating
customer_rating
```

---

# 🧩 Chapter 13 — Dimension Tables

Our current dimensions are:

```text
dim_date
dim_customer
dim_vehicle
dim_location
```

Dimensions provide context.

For example:

```text
fact_rides
    vehicle_key
        ↓
dim_vehicle
    vehicle_type = Go Sedan
```

The fact table stores the relationship.

The dimension stores descriptive information.

---

# 🔑 Chapter 14 — Surrogate Keys

Our warehouse uses surrogate keys such as:

```text
customer_key
vehicle_key
location_key
date_key
```

These are warehouse-generated identifiers.

They are different from source/business identifiers such as:

```text
customer_id
booking_id
```

This separation is useful because source identifiers can have unexpected properties.

We already discovered that `booking_id` is not unique.

---

# 📅 Chapter 15 — Date Dimension

We created:

```text
dim_date
```

with attributes including:

```text
date_key
full_date
year
month
day
day_of_week
day_name
```

A date dimension allows us to perform time-based analysis easily.

For example:

```sql
GROUP BY year, month
```

or:

```sql
GROUP BY day_name
```

without repeatedly deriving those attributes from timestamps.

---

# 🗺️ Chapter 16 — Location Dimension

We created:

```text
dim_location
```

from both:

```text
pickup_location
drop_location
```

A single location dimension is reused twice.

The fact table contains:

```text
pickup_location_key
drop_location_key
```

Both point to:

```text
dim_location
```

This is called a **role-playing dimension**.

The same dimension plays two roles:

```text
Location → Pickup
Location → Dropoff
```

---

# 🧪 Chapter 17 — Data Quality

Data quality is more than checking whether a database query succeeds.

We performed checks such as:

- valid rating ranges
- completed rides have booking value
- completed rides have ride distance
- cancellation reasons are present when expected
- cancelled/no-driver rides do not incorrectly contain financial ride measures
- foreign keys can be reconciled
- staging and fact row counts match

The principle is:

```text
Understand
    ↓
Validate
    ↓
Enforce
```

---

# 🔗 Chapter 18 — Referential Integrity

The fact table references dimensions.

For example:

```text
fact_rides.customer_key
        ↓
dim_customer.customer_key
```

We validate that these relationships work.

A broken relationship would mean:

```text
Fact
 ↓
customer_key = 123
 ↓
No matching customer
```

That is a warehouse integrity problem.

Our current validation checks ensure these relationships are valid.

---

# 🔄 Chapter 19 — Idempotency

Idempotency is one of the most important pipeline concepts we have implemented.

It means:

> Running the same pipeline repeatedly should produce the same correct result.

Without idempotency:

```text
Run 1 → 150,000
Run 2 → 300,000
Run 3 → 450,000
```

With our current full-refresh design:

```text
Run 1 → 150,000
Run 2 → 150,000
Run 3 → 150,000
```

The transformed warehouse is rebuilt from RAW.

---

# 🔁 Chapter 20 — Full Refresh

Our current pipeline uses a full-refresh strategy for the transformed layers.

Conceptually:

```text
RAW
 ↓
TRUNCATE STAGING
 ↓
Reload STAGING
 ↓
Rebuild Dimensions
 ↓
Rebuild Fact
 ↓
Validate
 ↓
COMMIT
```

This is simple and appropriate for our learning project and relatively small dataset.

It is not necessarily the best strategy for very large production datasets.

Later we will learn incremental loading.

---

# 💾 Chapter 21 — Transactions

The warehouse refresh runs inside a database transaction.

Conceptually:

```text
BEGIN
  ↓
Clear old transformed data
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

If something fails:

```text
ERROR
  ↓
ROLLBACK
```

This protects the warehouse from being left in a partially refreshed state.

---

# 🧪 Chapter 22 — Automated Validation

Our Python warehouse refresh now runs validation checks before committing.

Current checks include:

### Row counts

```text
STAGING == FACT
```

Expected:

```text
150,000 == 150,000
```

### Date keys

Expected invalid keys:

```text
0
```

### Customer keys

Expected invalid keys:

```text
0
```

### Vehicle keys

Expected invalid keys:

```text
0
```

### Location keys

Expected invalid keys:

```text
0
```

The pipeline therefore follows:

```text
Build
 ↓
Validate
 ↓
Commit
```

instead of:

```text
Build
 ↓
Commit
```

---

# 📊 Chapter 23 — Analytics Layer

We created an analytics schema:

```text
analytics
```

The analytics layer exposes reusable business-oriented views.

Current views include:

```text
analytics.booking_summary
analytics.daily_ride_metrics
analytics.vehicle_performance
```

---

# 📈 Booking Summary

The booking summary provides:

- total bookings
- completed bookings
- customer cancellations
- driver cancellations
- no-driver-found bookings
- incomplete bookings
- completion rate

The dataset's completion rate is:

```text
93,000 / 150,000 = 62%
```

---

# 📅 Daily Ride Metrics

The daily metrics view provides:

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

This is a dashboard-friendly analytical dataset.

---

# 🚗 Vehicle Performance

The vehicle performance view provides:

```text
vehicle_type
completed_rides
completed_revenue
avg_revenue_per_ride
```

Example:

| Vehicle | Completed Rides | Revenue | Avg Revenue/Ride |
|---|---:|---:|---:|
| Auto | 23,155 | 11,727,615 | 506.48 |
| Go Mini | 18,549 | 9,411,418 | 507.38 |
| Go Sedan | 16,676 | 8,538,560 | 512.03 |
| Bike | 14,034 | 7,144,913 | 509.11 |
| Premier Sedan | 11,252 | 5,733,655 | 509.57 |
| eBike | 6,551 | 3,298,157 | 503.46 |
| Uber XL | 2,783 | 1,406,256 | 505.30 |

An important observation:

> Total revenue is largely driven by completed ride volume because average revenue per ride is relatively similar across vehicle types.

---

# 🐳 Chapter 24 — Docker

PostgreSQL runs in Docker.

Docker helps us create a repeatable local environment.

Current architecture:

```text
Windows
  ↓
Docker
  ↓
PostgreSQL container
  ↓
taxi_data database
```

Docker Compose manages the PostgreSQL service.

---

# 🗂️ Current Project Structure

```text
taxi-data-engineering/
│
├── data/
│   └── ncr_ride_bookings.csv
│
├── src/
│   ├── load_raw.py
│   └── refresh_warehouse.py
│
├── sql/
│   ├── table creation scripts
│   ├── analytics scripts
│   └── vehicle performance script
│
├── tests/
│
├── docker-compose.yml
│
└── README.md
```

---

# ▶️ Running the Current Pipeline

## Start PostgreSQL

```powershell
docker compose up -d
```

Check:

```powershell
docker compose ps
```

---

## Connect to PostgreSQL

```powershell
docker compose exec postgres psql -U data_engineer -d taxi_data
```

---

## Load RAW

```powershell
python src/load_raw.py
```

---

## Refresh warehouse

```powershell
python src/refresh_warehouse.py
```

The refresh script performs:

```text
RAW
 ↓
STAGING
 ↓
DIMENSIONS
 ↓
FACT
 ↓
VALIDATION
 ↓
COMMIT
```

---

# 📌 Current Verified Warehouse State

The current pipeline produces:

```text
STAGING records       150,000
CUSTOMERS             148,788
VEHICLE TYPES               7
LOCATIONS                   176
FACT Rides             150,000
```

The pipeline was run repeatedly and these counts remained stable.

---

# 🧠 Important Lessons So Far

## Lesson 1

**Don't trust source data blindly.**

Profile it first.

---

## Lesson 2

**Don't assume identifiers are unique.**

Verify uniqueness.

---

## Lesson 3

**Don't treat every NULL as an error.**

Understand the business context.

---

## Lesson 4

**Keep RAW data.**

It provides a recovery and audit point.

---

## Lesson 5

**Define fact-table grain before designing the fact table.**

---

## Lesson 6

**Dimensions provide context; facts provide measurements and relationships.**

---

## Lesson 7

**Pipelines should be idempotent.**

A retry should not silently duplicate data.

---

## Lesson 8

**A successful SQL execution does not necessarily mean a successful pipeline.**

Data-quality checks are required.

---

## Lesson 9

**Transactions protect consistency.**

Build → Validate → Commit is safer than blindly committing every step.

---

## Lesson 10

**Start simple and add complexity deliberately.**

A strong data engineer understands why a technology is needed before introducing it.

---

# 🚧 What's Next?

The current core batch pipeline is complete.

The next phases will make it increasingly production-like.

---

## Phase 1 — Automated Testing

We will move beyond checks inside the refresh script.

We'll learn:

- unit tests
- integration tests
- data-quality tests
- business-rule tests
- test fixtures
- failure scenarios

---

## Phase 2 — Logging

Instead of only printing:

```text
Warehouse refreshed successfully
```

we will capture:

- execution time
- row counts
- failures
- warnings
- stages
- errors

Eventually:

```text
Pipeline started
 ↓
RAW loaded: 150000
 ↓
STAGING loaded: 150000
 ↓
FACT loaded: 150000
 ↓
Validation passed
 ↓
Pipeline completed
```

---

## Phase 3 — Apache Airflow

Airflow will become our orchestration layer.

Instead of manually running scripts:

```text
python load_raw.py
python refresh_warehouse.py
```

Airflow will manage dependencies:

```text
        Extract
           ↓
       Load RAW
           ↓
     Refresh Warehouse
           ↓
       Validate
           ↓
       Analytics
```

We'll learn:

- DAGs
- tasks
- dependencies
- scheduling
- retries
- backfills
- failure handling

---

## Phase 4 — dbt

We will introduce dbt for SQL-based transformations.

The architecture will evolve toward:

```text
RAW
 ↓
STAGING
 ↓
dbt models
 ↓
Dimensions / Facts
 ↓
Analytics
```

We'll learn:

- sources
- models
- tests
- documentation
- lineage
- incremental models
- macros

---

## Phase 5 — Incremental Data Loading

Our current system uses full refresh.

Later we'll learn how to process only new or changed data.

Topics:

- incremental loads
- watermarks
- upserts
- MERGE
- deduplication
- late-arriving data
- Change Data Capture
- Slowly Changing Dimensions

---

## Phase 6 — Data Lake

We'll introduce object storage.

Possible architecture:

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

- Amazon S3
- Azure Data Lake Storage
- Google Cloud Storage

---

## Phase 7 — Apache Spark

When datasets become too large for simple single-machine processing, we'll introduce Spark/PySpark.

We'll learn:

- Spark DataFrames
- transformations
- actions
- partitions
- shuffles
- joins
- caching
- performance optimization

---

## Phase 8 — Cloud

Eventually this local project will be deployed using cloud services.

We'll learn how:

```text
Local Docker
```

evolves into:

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

---

## Phase 9 — CI/CD

GitHub Actions will eventually automate:

```text
Git Push
   ↓
Run Tests
   ↓
Lint
   ↓
Build
   ↓
Deploy
```

This introduces software-engineering practices into data engineering.

---

## Phase 10 — Dashboard

The final analytics layer will feed a dashboard.

Potential KPIs:

```text
Total Bookings
Completion Rate
Cancellation Rate
Revenue
Average Revenue per Ride
Ride Distance
Revenue by Vehicle
Revenue by Location
Daily Booking Trends
Cancellation Reasons
Driver Ratings
Customer Ratings
```

Possible tools:

- Power BI
- Tableau
- Streamlit

---

# 🏁 Target Architecture

The eventual architecture is planned to become:

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


                 ┌───────────────────┐
                 │      AIRFLOW      │
                 │   ORCHESTRATION   │
                 └───────────────────┘


                 ┌───────────────────┐
                 │    GITHUB / CI    │
                 │       / CD        │
                 └───────────────────┘
```

This is the destination.

We will build it one concept at a time.

---

# 👥 Who Is This Repository For?

This repository is especially useful for:

### Beginners

People who are asking:

> "What exactly does a data engineer do?"

### Students

People who know some Python or SQL but have never built an end-to-end pipeline.

### Aspiring Data Engineers

People preparing for:

- data engineering projects
- interviews
- portfolio development
- real-world engineering work

### Experienced Developers Moving Into Data

Software engineers who want to understand:

- ETL
- warehouses
- dimensional modeling
- orchestration
- analytics engineering

---

# 📖 How To Learn From This Repository

Don't just copy the code.

For every stage, ask:

### 1. What problem are we solving?

### 2. Why did we choose this architecture?

### 3. Why is this table needed?

### 4. What happens if the pipeline fails?

### 5. What happens if we run it twice?

### 6. How do we know the output is correct?

### 7. How would this change with 1 billion rows?

### 8. How would this change if the source were an API?

### 9. How would this run automatically every day?

These questions are what turn tool knowledge into data-engineering knowledge.

---

# 🧭 Recommended Learning Path For Beginners

If you are completely new to data engineering, learn in this order:

```text
Python basics
      ↓
SQL basics
      ↓
PostgreSQL
      ↓
Git / GitHub
      ↓
CSV / JSON / APIs
      ↓
ETL / ELT
      ↓
Data Cleaning
      ↓
Data Modeling
      ↓
Fact & Dimension Tables
      ↓
Data Warehousing
      ↓
Data Quality
      ↓
Testing
      ↓
Docker
      ↓
Airflow
      ↓
dbt
      ↓
Cloud Storage
      ↓
Spark
      ↓
Cloud Platforms
      ↓
CI/CD
```

You do not need to master everything before starting the project.

Learn each concept when the project needs it.

---

# 💡 Engineering Principle

A major goal of this project is to develop the habit of asking:

> **"Why?"**

Not:

> "Which command do I copy?"

For example:

Instead of simply learning:

```sql
CREATE TABLE fact_rides ...
```

understand:

- What is a fact?
- What is the grain?
- Why are dimensions separate?
- Why use surrogate keys?
- Why shouldn't Booking ID be the primary key?
- Why do we need RAW?
- Why do we need STAGING?
- Why do we validate before committing?

That understanding is much more valuable than memorizing syntax.

---

# 📌 Current Status

```text
Core batch pipeline                  ✅
Python ingestion                     ✅
PostgreSQL warehouse                 ✅
Docker environment                   ✅
RAW layer                            ✅
STAGING layer                        ✅
Data profiling                       ✅
Data quality investigation           ✅
Star schema                          ✅
Date dimension                       ✅
Customer dimension                   ✅
Vehicle dimension                    ✅
Location dimension                   ✅
Fact table                            ✅
Analytics views                      ✅
Full refresh                          ✅
Idempotent refresh                   ✅
Transaction handling                 ✅
Automated warehouse validation       ✅
```

Coming next:

```text
Automated testing                    🚧
Logging                              🚧
Observability                        🚧
Airflow                              📋
dbt                                  📋
Incremental pipelines                📋
Data lake                            📋
Spark                                📋
Cloud                                📋
CI/CD                                📋
Dashboard                            📋
```

---

# 🤝 Contributing

If this repository is useful to you and you find:

- an error
- a better explanation
- a broken query
- an improvement
- a missing concept
- a better engineering approach

feel free to open an issue or pull request.

The goal is for this repository to become a useful **community learning resource**, not just a personal project.

---

# ⭐ Final Message

Data engineering can look overwhelming because the ecosystem contains many technologies.

You may see:

```text
Python
SQL
PostgreSQL
Airflow
dbt
Spark
Kafka
AWS
Azure
GCP
Docker
Kubernetes
Terraform
GitHub Actions
...
```

It is easy to think:

> "I need to learn all of this before I can become a data engineer."

You don't.

Start with:

```text
Python
 +
SQL
 +
Databases
 +
Data Modeling
 +
ETL/ELT
```

Then build.

Once you understand the problems, the tools become much easier to understand.

This repository follows exactly that philosophy:

```text
Learn
 ↓
Understand
 ↓
Build
 ↓
Validate
 ↓
Improve
 ↓
Scale
```

**The goal is not to build the most complicated pipeline.**

**The goal is to understand why a good pipeline is designed the way it is.**
