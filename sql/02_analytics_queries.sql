-- Relational Joins & Aggregations
SELECT 
    f.facility_name,
    f.operating_region,
    s.sensor_type,
    COUNT(t.reading_id) AS total_readings,
    ROUND(AVG(t.reading_value), 2) AS avg_consumption,
    s.unit_of_measure
FROM fact_telemetry_readings t
JOIN dim_sensors s ON t.sensor_id = s.sensor_id
JOIN dim_facilities f ON s.facility_id = f.facility_id
GROUP BY f.facility_name, s.sensor_type, s.unit_of_measure;

-- Window Function: Spike Surge Detection via LAG()
WITH TelemetryLagCTE AS (
    SELECT 
        reading_id,
        sensor_id,
        reading_timestamp,
        reading_value,
        LAG(reading_value, 1) OVER (
            PARTITION BY sensor_id 
            ORDER BY reading_timestamp
        ) AS previous_reading
    FROM fact_telemetry_readings
)
SELECT 
    sensor_id,
    reading_timestamp,
    previous_reading,
    reading_value AS current_reading,
    ROUND(((reading_value - previous_reading) / previous_reading) * 100, 2) AS pct_surge
FROM TelemetryLagCTE
WHERE previous_reading IS NOT NULL 
  AND ((reading_value - previous_reading) / previous_reading) > 0.20;
