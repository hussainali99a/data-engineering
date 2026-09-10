import psycopg2

from src.config import DB_CONFIG

def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def test_staging_and_fact_row_count():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT COUNT(*) FROM stg_ncr_ride_bookings;"
            )
            staging_count = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM fact_rides;"
            )
            fact_count = cursor.fetchone()[0]

        assert staging_count == fact_count

    finally:
        connection.close()
        
        



def test_raw_and_staging_row_count():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute(
                "SELECT COUNT(*) FROM raw_ncr_ride_bookings;"
            )
            raw_count = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM stg_ncr_ride_bookings;"
            )
            staging_count = cursor.fetchone()[0]

        assert raw_count == staging_count

    finally:
        connection.close()
        
        
        
def test_staging_raw_id_is_unique():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*)
                FROM stg_ncr_ride_bookings;
            """)
            total_rows = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(DISTINCT raw_id)
                FROM stg_ncr_ride_bookings;
            """)
            unique_raw_ids = cursor.fetchone()[0]

        assert total_rows == unique_raw_ids

    finally:
        connection.close()
        


def test_vehicle_dimension_is_unique():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*)
                FROM dim_vehicle;
            """)
            total_rows = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(DISTINCT vehicle_type)
                FROM dim_vehicle;
            """)
            unique_vehicle_types = cursor.fetchone()[0]

        assert total_rows == unique_vehicle_types

    finally:
        connection.close()
        

def test_customer_dimension_is_unique():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*)
                FROM dim_customer;
            """)
            total_rows = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(DISTINCT customer_id)
                FROM dim_customer;
            """)
            unique_customer_ids = cursor.fetchone()[0]

        assert total_rows == unique_customer_ids

    finally:
        connection.close()
        
        
        
def test_location_dimension_is_unique():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*)
                FROM dim_location;
            """)
            total_rows = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(DISTINCT location_name)
                FROM dim_location;
            """)
            unique_locations = cursor.fetchone()[0]

        assert total_rows == unique_locations

    finally:
        connection.close()
        
        

def test_fact_customer_keys_are_valid():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*)
                FROM fact_rides f
                LEFT JOIN dim_customer c
                    ON f.customer_key = c.customer_key
                WHERE c.customer_key IS NULL;
            """)

            broken_keys = cursor.fetchone()[0]

        assert broken_keys == 0

    finally:
        connection.close()
        
        
def test_fact_vehicle_keys_are_valid():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*)
                FROM fact_rides f
                LEFT JOIN dim_vehicle v
                    ON f.vehicle_key = v.vehicle_key
                WHERE v.vehicle_key IS NULL;
            """)

            broken_keys = cursor.fetchone()[0]

        assert broken_keys == 0

    finally:
        connection.close()
        
        
def test_fact_date_keys_are_valid():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*)
                FROM fact_rides f
                LEFT JOIN dim_date d
                    ON f.date_key = d.date_key
                WHERE d.date_key IS NULL;
            """)

            broken_keys = cursor.fetchone()[0]

        assert broken_keys == 0

    finally:
        connection.close()
        

def test_fact_pickup_location_keys_are_valid():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*)
                FROM fact_rides f
                LEFT JOIN dim_location l
                    ON f.pickup_location_key = l.location_key
                WHERE l.location_key IS NULL;
            """)

            broken_keys = cursor.fetchone()[0]

        assert broken_keys == 0

    finally:
        connection.close()
        

def test_fact_drop_location_keys_are_valid():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*)
                FROM fact_rides f
                LEFT JOIN dim_location l
                    ON f.drop_location_key = l.location_key
                WHERE l.location_key IS NULL;
            """)

            broken_keys = cursor.fetchone()[0]

        assert broken_keys == 0

    finally:
        connection.close()
        
        
def test_completed_rides_have_booking_value_and_distance():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*)
                FROM fact_rides
                WHERE booking_status = 'Completed'
                  AND (
                      booking_value IS NULL
                      OR ride_distance IS NULL
                  );
            """)

            invalid_rows = cursor.fetchone()[0]

        assert invalid_rows == 0

    finally:
        connection.close()
        

def test_cancelled_rides_do_not_have_value_or_distance():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*)
                FROM fact_rides
                WHERE booking_status IN (
                    'Cancelled by Customer',
                    'Cancelled by Driver',
                    'No Driver Found'
                )
                AND (
                    booking_value IS NOT NULL
                    OR ride_distance IS NOT NULL
                );
            """)

            invalid_rows = cursor.fetchone()[0]

        assert invalid_rows == 0

    finally:
        connection.close()
        
        
def test_ratings_are_within_valid_range():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*)
                FROM fact_rides
                WHERE
                    (driver_rating IS NOT NULL
                     AND (driver_rating < 3 OR driver_rating > 5))
                    OR
                    (customer_rating IS NOT NULL
                     AND (customer_rating < 3 OR customer_rating > 5));
            """)

            invalid_rows = cursor.fetchone()[0]

        assert invalid_rows == 0

    finally:
        connection.close()
        
        


def test_customer_cancellations_have_reason():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*)
                FROM stg_ncr_ride_bookings
                WHERE booking_status = 'Cancelled by Customer'
                  AND reason_for_cancelling_by_customer IS NULL;
            """)

            invalid_rows = cursor.fetchone()[0]

        assert invalid_rows == 0

    finally:
        connection.close()
        
        


def test_driver_cancellations_have_reason():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*)
                FROM stg_ncr_ride_bookings
                WHERE booking_status = 'Cancelled by Driver'
                  AND driver_cancellation_reason IS NULL;
            """)

            invalid_rows = cursor.fetchone()[0]

        assert invalid_rows == 0

    finally:
        connection.close()
        
        

def test_booking_statuses_are_valid():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT DISTINCT booking_status
                FROM stg_ncr_ride_bookings
                WHERE booking_status IS NOT NULL;
            """)

            actual_statuses = {
                row[0]
                for row in cursor.fetchall()
            }

        expected_statuses = {
            'Completed',
            'Cancelled by Driver',
            'Cancelled by Customer',
            'No Driver Found',
            'Incomplete'
        }

        assert actual_statuses == expected_statuses

    finally:
        connection.close()
        


def test_fact_required_keys_are_not_null():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT COUNT(*)
                FROM fact_rides
                WHERE date_key IS NULL
                   OR customer_key IS NULL
                   OR vehicle_key IS NULL
                   OR pickup_location_key IS NULL
                   OR drop_location_key IS NULL;
            """)

            invalid_rows = cursor.fetchone()[0]

        assert invalid_rows == 0

    finally:
        connection.close()