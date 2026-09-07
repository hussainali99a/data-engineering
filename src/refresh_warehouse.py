import psycopg2


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "taxi_data",
    "user": "data_engineer",
    "password": "data_engineering",
}


def validate_warehouse(cursor):
    """
    Run data-quality checks after rebuilding the warehouse.

    If any check fails, raise an exception.
    The calling function will then roll back the transaction.
    """

    print("Running data-quality checks...")

    # ---------------------------------------------------------
    # Check 1: STAGING and FACT should have the same row count
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT
            (SELECT COUNT(*) FROM stg_ncr_ride_bookings),
            (SELECT COUNT(*) FROM fact_rides);
    """)

    staging_count, fact_count = cursor.fetchone()

    if staging_count != fact_count:
        raise ValueError(
            f"Row count mismatch: "
            f"staging={staging_count}, fact={fact_count}"
        )

    print(f"✓ Row counts match: {staging_count}")

    # ---------------------------------------------------------
    # Check 2: Every fact row should have a valid date key
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT COUNT(*)
        FROM fact_rides f
        LEFT JOIN dim_date d
            ON f.date_key = d.date_key
        WHERE d.date_key IS NULL;
    """)

    broken_dates = cursor.fetchone()[0]

    if broken_dates != 0:
        raise ValueError(
            f"Found {broken_dates} fact rows with invalid date keys"
        )

    print("✓ Date keys valid")

    # ---------------------------------------------------------
    # Check 3: Every fact row should have a valid customer key
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT COUNT(*)
        FROM fact_rides f
        LEFT JOIN dim_customer c
            ON f.customer_key = c.customer_key
        WHERE c.customer_key IS NULL;
    """)

    broken_customers = cursor.fetchone()[0]

    if broken_customers != 0:
        raise ValueError(
            f"Found {broken_customers} fact rows with invalid customer keys"
        )

    print("✓ Customer keys valid")

    # ---------------------------------------------------------
    # Check 4: Every fact row should have a valid vehicle key
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT COUNT(*)
        FROM fact_rides f
        LEFT JOIN dim_vehicle v
            ON f.vehicle_key = v.vehicle_key
        WHERE v.vehicle_key IS NULL;
    """)

    broken_vehicles = cursor.fetchone()[0]

    if broken_vehicles != 0:
        raise ValueError(
            f"Found {broken_vehicles} fact rows with invalid vehicle keys"
        )

    print("✓ Vehicle keys valid")

    # ---------------------------------------------------------
    # Check 5: Every fact row should have valid locations
    # ---------------------------------------------------------
    cursor.execute("""
        SELECT COUNT(*)
        FROM fact_rides f

        LEFT JOIN dim_location pickup
            ON f.pickup_location_key = pickup.location_key

        LEFT JOIN dim_location dropoff
            ON f.drop_location_key = dropoff.location_key

        WHERE pickup.location_key IS NULL
           OR dropoff.location_key IS NULL;
    """)

    broken_locations = cursor.fetchone()[0]

    if broken_locations != 0:
        raise ValueError(
            f"Found {broken_locations} fact rows with invalid location keys"
        )

    print("✓ Location keys valid")

    # ---------------------------------------------------------
    # All checks passed
    # ---------------------------------------------------------
    print("All data-quality checks passed.")


def refresh_warehouse():
    """
    Rebuild the warehouse from the RAW layer.

    This uses a full-refresh strategy:
        RAW → STAGING → DIMENSIONS → FACT

    Everything is performed inside one database transaction.
    """

    connection = psycopg2.connect(**DB_CONFIG)

    try:

        with connection.cursor() as cursor:

            # =====================================================
            # 1. Remove previously transformed data
            # =====================================================

            print("Clearing transformed tables...")

            cursor.execute(
                "TRUNCATE TABLE fact_rides RESTART IDENTITY;"
            )

            cursor.execute(
                "TRUNCATE TABLE dim_location RESTART IDENTITY;"
            )

            cursor.execute(
                "TRUNCATE TABLE dim_customer RESTART IDENTITY;"
            )

            cursor.execute(
                "TRUNCATE TABLE dim_vehicle RESTART IDENTITY;"
            )

            cursor.execute(
                "TRUNCATE TABLE stg_ncr_ride_bookings;"
            )

            print("Transformed tables cleared.")

            # =====================================================
            # 2. RAW → STAGING
            # =====================================================

            print("Loading STAGING from RAW...")

            cursor.execute("""
                INSERT INTO stg_ncr_ride_bookings (
                    raw_id,
                    booking_date,
                    booking_time,
                    booking_datetime,
                    booking_id,
                    booking_status,
                    customer_id,
                    vehicle_type,
                    pickup_location,
                    drop_location,
                    avg_vtat,
                    avg_ctat,
                    cancelled_rides_by_customer,
                    reason_for_cancelling_by_customer,
                    cancelled_rides_by_driver,
                    driver_cancellation_reason,
                    incomplete_rides,
                    incomplete_rides_reason,
                    booking_value,
                    ride_distance,
                    driver_rating,
                    customer_rating,
                    payment_method
                )

                SELECT
                    raw_id,

                    NULLIF(TRIM(date), 'null')::DATE,

                    NULLIF(TRIM(time), 'null')::TIME,

                    (
                        NULLIF(TRIM(date), 'null')
                        || ' '
                        || NULLIF(TRIM(time), 'null')
                    )::TIMESTAMP,

                    TRIM(BOTH '"' FROM booking_id),

                    NULLIF(TRIM(booking_status), 'null'),

                    TRIM(BOTH '"' FROM customer_id),

                    NULLIF(TRIM(vehicle_type), 'null'),

                    NULLIF(TRIM(pickup_location), 'null'),

                    NULLIF(TRIM(drop_location), 'null'),

                    NULLIF(TRIM(avg_vtat), 'null')::NUMERIC(10, 2),

                    NULLIF(TRIM(avg_ctat), 'null')::NUMERIC(10, 2),

                    NULLIF(
                        TRIM(cancelled_rides_by_customer),
                        'null'
                    )::INTEGER,

                    NULLIF(
                        TRIM(reason_for_cancelling_by_customer),
                        'null'
                    ),

                    NULLIF(
                        TRIM(cancelled_rides_by_driver),
                        'null'
                    )::INTEGER,

                    NULLIF(
                        TRIM(driver_cancellation_reason),
                        'null'
                    ),

                    NULLIF(
                        TRIM(incomplete_rides),
                        'null'
                    )::INTEGER,

                    NULLIF(
                        TRIM(incomplete_rides_reason),
                        'null'
                    ),

                    NULLIF(
                        TRIM(booking_value),
                        'null'
                    )::NUMERIC(10, 2),

                    NULLIF(
                        TRIM(ride_distance),
                        'null'
                    )::NUMERIC(10, 2),

                    NULLIF(
                        TRIM(driver_ratings),
                        'null'
                    )::NUMERIC(2, 1),

                    NULLIF(
                        TRIM(customer_rating),
                        'null'
                    )::NUMERIC(2, 1),

                    NULLIF(
                        TRIM(payment_method),
                        'null'
                    )

                FROM raw_ncr_ride_bookings;
            """)

            print("STAGING loaded.")

            # =====================================================
            # 3. Build VEHICLE dimension
            # =====================================================

            print("Building vehicle dimension...")

            cursor.execute("""
                INSERT INTO dim_vehicle (vehicle_type)

                SELECT DISTINCT
                    vehicle_type

                FROM stg_ncr_ride_bookings

                WHERE vehicle_type IS NOT NULL

                ORDER BY vehicle_type;
            """)

            print("Vehicle dimension built.")

            # =====================================================
            # 4. Build CUSTOMER dimension
            # =====================================================

            print("Building customer dimension...")

            cursor.execute("""
                INSERT INTO dim_customer (customer_id)

                SELECT DISTINCT
                    customer_id

                FROM stg_ncr_ride_bookings

                WHERE customer_id IS NOT NULL

                ORDER BY customer_id;
            """)

            print("Customer dimension built.")

            # =====================================================
            # 5. Build LOCATION dimension
            # =====================================================

            print("Building location dimension...")

            cursor.execute("""
                INSERT INTO dim_location (location_name)

                SELECT DISTINCT
                    location_name

                FROM (
                    SELECT
                        pickup_location AS location_name

                    FROM stg_ncr_ride_bookings

                    UNION

                    SELECT
                        drop_location AS location_name

                    FROM stg_ncr_ride_bookings
                ) locations

                WHERE location_name IS NOT NULL

                ORDER BY location_name;
            """)

            print("Location dimension built.")

            # =====================================================
            # 6. Build FACT table
            # =====================================================

            print("Building fact table...")

            cursor.execute("""
                INSERT INTO fact_rides (
                    raw_id,
                    booking_id,
                    date_key,
                    customer_key,
                    vehicle_key,
                    pickup_location_key,
                    drop_location_key,
                    booking_status,
                    booking_value,
                    ride_distance,
                    avg_vtat,
                    avg_ctat,
                    driver_rating,
                    customer_rating,
                    cancelled_rides_by_customer,
                    cancelled_rides_by_driver,
                    incomplete_rides
                )

                SELECT
                    s.raw_id,
                    s.booking_id,

                    d.date_key,

                    c.customer_key,

                    v.vehicle_key,

                    pickup.location_key,

                    dropoff.location_key,

                    s.booking_status,

                    s.booking_value,

                    s.ride_distance,

                    s.avg_vtat,

                    s.avg_ctat,

                    s.driver_rating,

                    s.customer_rating,

                    s.cancelled_rides_by_customer,

                    s.cancelled_rides_by_driver,

                    s.incomplete_rides

                FROM stg_ncr_ride_bookings s

                JOIN dim_date d
                    ON s.booking_date = d.full_date

                JOIN dim_customer c
                    ON s.customer_id = c.customer_id

                JOIN dim_vehicle v
                    ON s.vehicle_type = v.vehicle_type

                JOIN dim_location pickup
                    ON s.pickup_location = pickup.location_name

                JOIN dim_location dropoff
                    ON s.drop_location = dropoff.location_name;
            """)

            print("Fact table built.")

            # =====================================================
            # 7. Validate warehouse
            # =====================================================

            validate_warehouse(cursor)

        # =========================================================
        # 8. Commit transaction
        # =========================================================

        connection.commit()

        print("Warehouse refreshed successfully.")

    except Exception as error:

        # =========================================================
        # 9. Roll back transaction if anything fails
        # =========================================================

        connection.rollback()

        print("Warehouse refresh failed.")
        print(f"Error: {error}")

        raise

    finally:

        # =========================================================
        # 10. Always close database connection
        # =========================================================

        connection.close()


if __name__ == "__main__":
    refresh_warehouse()