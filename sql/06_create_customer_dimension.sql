CREATE TABLE IF NOT EXISTS dim_customer (
    customer_key SERIAL PRIMARY KEY,
    customer_id TEXT NOT NULL UNIQUE
);

INSERT INTO dim_customer (customer_id)
SELECT DISTINCT customer_id
FROM stg_ncr_ride_bookings
WHERE customer_id IS NOT NULL
ORDER BY customer_id;
