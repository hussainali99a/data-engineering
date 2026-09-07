CREATE OR REPLACE VIEW analytics.vehicle_performance AS
SELECT
    v.vehicle_type,

    COUNT(*) FILTER (
        WHERE f.booking_status = 'Completed'
    ) AS completed_rides,

    COALESCE(
        SUM(f.booking_value) FILTER (
            WHERE f.booking_status = 'Completed'
        ),
        0
    ) AS completed_revenue,

    ROUND(
        COALESCE(
            SUM(f.booking_value) FILTER (
                WHERE f.booking_status = 'Completed'
            ),
            0
        )
        /
        NULLIF(
            COUNT(*) FILTER (
                WHERE f.booking_status = 'Completed'
            ),
            0
        ),
        2
    ) AS avg_revenue_per_ride

FROM fact_rides f
JOIN dim_vehicle v
    ON f.vehicle_key = v.vehicle_key

GROUP BY v.vehicle_type;