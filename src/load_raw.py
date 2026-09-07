import csv
import psycopg2


CSV_FILE = r"D:\taxi-data-engineering\data\ncr_ride_bookings.csv"


DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "taxi_data",
    "user": "data_engineer",
    "password": "data_engineering",
}


def load_data():
    connection = psycopg2.connect(**DB_CONFIG)

    try:
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE TABLE raw_ncr_ride_bookings;")
            
            with open(CSV_FILE, "r", encoding="utf-8") as file:

                cursor.copy_expert(
                    """
                    COPY raw_ncr_ride_bookings (
                        date,
                        time,
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
                        driver_ratings,
                        customer_rating,
                        payment_method
                    )
                    FROM STDIN
                    WITH CSV HEADER
                    """,
                    file
                )

        connection.commit()

        print("Data loaded successfully.")

    except Exception as error:
        connection.rollback()
        print("Error loading data:")
        print(error)
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    load_data()