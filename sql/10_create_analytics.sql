CREATE SCHEMA IF NOT EXISTS analytics;


CREATE OR REPLACE VIEW analytics.booking_summary AS
SELECT
    COUNT(*) AS total_bookings,

    COUNT(*) FILTER (
        WHERE booking_status = 'Completed'
    ) AS completed_bookings,

    COUNT(*) FILTER (
        WHERE booking_status = 'Cancelled by Customer'
    ) AS customer_cancellations,

    COUNT(*) FILTER (
        WHERE booking_status = 'Cancelled by Driver'
    ) AS driver_cancellations,

    COUNT(*) FILTER (
        WHERE booking_status = 'No Driver Found'
    ) AS no_driver_found,

    COUNT(*) FILTER (
        WHERE booking_status = 'Incomplete'
    ) AS incomplete_bookings,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE booking_status = 'Completed'
        ) / COUNT(*),
        2
    ) AS completion_rate_pct

FROM fact_rides;



CREATE OR REPLACE VIEW analytics.daily_ride_metrics AS
SELECT
    d.full_date,
    d.year,
    d.month,
    d.day_name,

    COUNT(*) AS total_bookings,

    COUNT(*) FILTER (
        WHERE f.booking_status = 'Completed'
    ) AS completed_rides,

    COALESCE(
        SUM(f.booking_value) FILTER (
            WHERE f.booking_status = 'Completed'
        ),
        0
    ) AS completed_revenue,

    COALESCE(
        SUM(f.ride_distance) FILTER (
            WHERE f.booking_status = 'Completed'
        ),
        0
    ) AS completed_distance

FROM fact_rides f
JOIN dim_date d
    ON f.date_key = d.date_key

GROUP BY
    d.full_date,
    d.year,
    d.month,
    d.day_name;