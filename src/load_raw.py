import logging
import os
import time

import psycopg2

from src.config import DB_CONFIG


# CSV_FILE = r"D:\taxi-data-engineering\data\ncr_ride_bookings.csv"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "ncr_ride_bookings.csv"
)


# =========================================================
# Logging configuration
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/pipeline.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# =========================================================
# RAW data ingestion
# =========================================================

def load_data():

    start_time = time.time()

    logger.info("==========================================")
    logger.info("Starting RAW data ingestion")
    logger.info("==========================================")

    connection = None

    try:

        # -----------------------------------------------------
        # 1. Check CSV file
        # -----------------------------------------------------

        logger.info("Checking source CSV file...")

        if not os.path.exists(CSV_FILE):
            raise FileNotFoundError(
                f"CSV file not found: {CSV_FILE}"
            )

        logger.info("CSV file found: %s", CSV_FILE)

        # -----------------------------------------------------
        # 2. Connect to PostgreSQL
        # -----------------------------------------------------

        logger.info("Connecting to PostgreSQL...")

        connection = psycopg2.connect(**DB_CONFIG)

        logger.info("Connected to PostgreSQL successfully")

        with connection.cursor() as cursor:

            # -------------------------------------------------
            # 3. Clear previous RAW data
            # -------------------------------------------------

            logger.info(
                "Clearing existing RAW data "
                "for idempotent load..."
            )

            cursor.execute(
                "TRUNCATE TABLE raw_ncr_ride_bookings "
                "RESTART IDENTITY;"
            )

            logger.info("Existing RAW data cleared")

            # -------------------------------------------------
            # 4. Load CSV into RAW
            # -------------------------------------------------

            logger.info(
                "Loading CSV into raw_ncr_ride_bookings..."
            )

            with open(
                CSV_FILE,
                "r",
                encoding="utf-8"
            ) as file:

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

            logger.info(
                "CSV data loaded into RAW table"
            )

            # -------------------------------------------------
            # 5. Verify loaded row count
            # -------------------------------------------------

            logger.info(
                "Validating RAW row count..."
            )

            cursor.execute(
                "SELECT COUNT(*) "
                "FROM raw_ncr_ride_bookings;"
            )

            row_count = cursor.fetchone()[0]

            if row_count == 0:
                raise ValueError(
                    "RAW table contains 0 rows after ingestion"
                )

            logger.info(
                "RAW table contains %s rows",
                row_count,
            )

        # -----------------------------------------------------
        # 6. Commit transaction
        # -----------------------------------------------------

        logger.info(
            "Committing RAW ingestion transaction..."
        )

        connection.commit()

        elapsed_time = time.time() - start_time

        logger.info(
            "Transaction committed successfully"
        )

        logger.info(
            "RAW data ingestion completed successfully "
            "in %.2f seconds",
            elapsed_time,
        )

        logger.info("==========================================")


    # =========================================================
    # File-related errors
    # =========================================================

    except FileNotFoundError:

        logger.exception(
            "Source CSV file is missing"
        )

        raise


    # =========================================================
    # PostgreSQL/database errors
    # =========================================================

    except psycopg2.Error:

        if connection:
            connection.rollback()

            logger.info(
                "Database transaction rolled back"
            )

        logger.exception(
            "PostgreSQL/database error occurred "
            "during RAW ingestion"
        )

        raise


    # =========================================================
    # Data validation errors
    # =========================================================

    except ValueError:

        if connection:
            connection.rollback()

            logger.info(
                "Transaction rolled back due to "
                "data validation failure"
            )

        logger.exception(
            "Data validation error during RAW ingestion"
        )

        raise


    # =========================================================
    # Unexpected errors
    # =========================================================

    except Exception:

        if connection:
            connection.rollback()

            logger.info(
                "Transaction rolled back due to "
                "unexpected error"
            )

        logger.exception(
            "Unexpected error during RAW ingestion"
        )

        raise


    # =========================================================
    # Always close connection
    # =========================================================

    finally:

        if connection:
            connection.close()

            logger.info(
                "Database connection closed"
            )


# =========================================================
# Entry point
# =========================================================

if __name__ == "__main__":
    load_data()