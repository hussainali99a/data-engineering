CREATE TABLE IF NOT EXISTS dim_location (
    location_key SERIAL PRIMARY KEY,
    location_name TEXT NOT NULL UNIQUE
);

INSERT INTO dim_location (location_name)
SELECT DISTINCT location_name
FROM (
    SELECT pickup_location AS location_name
    FROM stg_ncr_ride_bookings

    UNION

    SELECT drop_location AS location_name
    FROM stg_ncr_ride_bookings
) locations
WHERE location_name IS NOT NULL
ORDER BY location_name;

