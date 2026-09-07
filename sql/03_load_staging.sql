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

    -- Date / time
    NULLIF(TRIM(date), 'null')::DATE,
    NULLIF(TRIM(time), 'null')::TIME,

    (
        NULLIF(TRIM(date), 'null') || ' ' ||
        NULLIF(TRIM(time), 'null')
    )::TIMESTAMP,

    -- IDs
    TRIM(BOTH '"' FROM booking_id),
    NULLIF(TRIM(booking_status), 'null'),
    TRIM(BOTH '"' FROM customer_id),

    -- Locations / vehicle
    NULLIF(TRIM(vehicle_type), 'null'),
    NULLIF(TRIM(pickup_location), 'null'),
    NULLIF(TRIM(drop_location), 'null'),

    -- Timing metrics
    NULLIF(TRIM(avg_vtat), 'null')::NUMERIC(10,2),
    NULLIF(TRIM(avg_ctat), 'null')::NUMERIC(10,2),

    -- Customer cancellation
    NULLIF(TRIM(cancelled_rides_by_customer), 'null')::INTEGER,
    NULLIF(TRIM(reason_for_cancelling_by_customer), 'null'),

    -- Driver cancellation
    NULLIF(TRIM(cancelled_rides_by_driver), 'null')::INTEGER,
    NULLIF(TRIM(driver_cancellation_reason), 'null'),

    -- Incomplete rides
    NULLIF(TRIM(incomplete_rides), 'null')::INTEGER,
    NULLIF(TRIM(incomplete_rides_reason), 'null'),

    -- Financial / distance
    NULLIF(TRIM(booking_value), 'null')::NUMERIC(10,2),
    NULLIF(TRIM(ride_distance), 'null')::NUMERIC(10,2),

    -- Ratings
    NULLIF(TRIM(driver_ratings), 'null')::NUMERIC(2,1),
    NULLIF(TRIM(customer_rating), 'null')::NUMERIC(2,1),

    -- Payment
    NULLIF(TRIM(payment_method), 'null')

FROM raw_ncr_ride_bookings;