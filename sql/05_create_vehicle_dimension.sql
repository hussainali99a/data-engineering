CREATE TABLE IF NOT EXISTS dim_vehicle (
    vehicle_key SERIAL PRIMARY KEY,
    vehicle_type TEXT NOT NULL UNIQUE
);



INSERT INTO dim_vehicle (vehicle_type)
SELECT DISTINCT vehicle_type
FROM stg_ncr_ride_bookings
WHERE vehicle_type IS NOT NULL
ORDER BY vehicle_type;