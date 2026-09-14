-- Enterprise Advanced Analytical Models & Window Aggregations

SELECT 
    f.facility_id,
    f.facility_name,
    s.sensor_type,
    t.reading_timestamp,
    t.reading_value,
    AVG(t.reading_value) OVER (
        PARTITION BY t.sensor_id 
        ORDER BY t.reading_timestamp 
        ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
    ) AS rolling_consumption_moving_avg
FROM fact_telemetry_readings t
JOIN dim_sensors s ON t.sensor_id = s.sensor_id
JOIN dim_facilities f ON s.facility_id = f.facility_id;

SELECT 
    f.operating_region,
    s.sensor_type,
    SUM(t.reading_value) AS regional_total_volume,
    DENSE_RANK() OVER (
        PARTITION BY s.sensor_type 
        ORDER BY SUM(t.reading_value) DESC
    ) AS regional_rank
FROM fact_telemetry_readings t
JOIN dim_sensors s ON t.sensor_id = s.sensor_id
JOIN dim_facilities f ON s.facility_id = f.facility_id
GROUP BY f.operating_region, s.sensor_type;
