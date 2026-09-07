CREATE TABLE IF NOT EXISTS raw_ncr_ride_bookings (
    raw_id BIGSERIAL PRIMARY KEY,

    date TEXT,
    time TEXT,
    booking_id TEXT,
    booking_status TEXT,
    customer_id TEXT,
    vehicle_type TEXT,
    pickup_location TEXT,
    drop_location TEXT,

    avg_vtat TEXT,
    avg_ctat TEXT,

    cancelled_rides_by_customer TEXT,
    reason_for_cancelling_by_customer TEXT,

    cancelled_rides_by_driver TEXT,
    driver_cancellation_reason TEXT,

    incomplete_rides TEXT,
    incomplete_rides_reason TEXT,

    booking_value TEXT,
    ride_distance TEXT,
    driver_ratings TEXT,
    customer_rating TEXT,
    payment_method TEXT,

    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);