CREATE TABLE IF NOT EXISTS stg_ncr_ride_bookings (
    raw_id BIGINT PRIMARY KEY,

    booking_date DATE,
    booking_time TIME,
    booking_datetime TIMESTAMP,

    booking_id TEXT,
    booking_status TEXT,
    customer_id TEXT,

    vehicle_type TEXT,
    pickup_location TEXT,
    drop_location TEXT,

    avg_vtat NUMERIC(10, 2),
    avg_ctat NUMERIC(10, 2),

    cancelled_rides_by_customer INTEGER,
    reason_for_cancelling_by_customer TEXT,

    cancelled_rides_by_driver INTEGER,
    driver_cancellation_reason TEXT,

    incomplete_rides INTEGER,
    incomplete_rides_reason TEXT,

    booking_value NUMERIC(10, 2),
    ride_distance NUMERIC(10, 2),

    driver_rating NUMERIC(2, 1),
    customer_rating NUMERIC(2, 1),

    payment_method TEXT,

    transformed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);