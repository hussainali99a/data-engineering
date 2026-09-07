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