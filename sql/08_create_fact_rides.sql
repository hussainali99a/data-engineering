CREATE TABLE IF NOT EXISTS fact_rides (
    ride_key BIGSERIAL PRIMARY KEY,

    raw_id BIGINT NOT NULL UNIQUE,
    booking_id TEXT NOT NULL,

    date_key INTEGER NOT NULL,
    customer_key INTEGER NOT NULL,
    vehicle_key INTEGER NOT NULL,
    pickup_location_key INTEGER NOT NULL,
    drop_location_key INTEGER NOT NULL,

    booking_status TEXT NOT NULL,

    booking_value NUMERIC(10, 2),
    ride_distance NUMERIC(10, 2),
    avg_vtat NUMERIC(10, 2),
    avg_ctat NUMERIC(10, 2),

    driver_rating NUMERIC(2, 1),
    customer_rating NUMERIC(2, 1),

    cancelled_rides_by_customer INTEGER,
    cancelled_rides_by_driver INTEGER,
    incomplete_rides INTEGER
);


