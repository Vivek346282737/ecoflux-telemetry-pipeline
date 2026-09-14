CREATE TABLE IF NOT EXISTS dim_facilities (
    facility_id VARCHAR(10) PRIMARY KEY,
    facility_name VARCHAR(100) NOT NULL,
    operating_region VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS dim_sensors (
    sensor_id VARCHAR(20) PRIMARY KEY,
    facility_id VARCHAR(10) NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    unit_of_measure VARCHAR(20) NOT NULL,
    FOREIGN KEY (facility_id) REFERENCES dim_facilities(facility_id)
);

CREATE TABLE IF NOT EXISTS fact_telemetry_readings (
    reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id VARCHAR(20) NOT NULL,
    reading_timestamp TIMESTAMP NOT NULL,
    reading_value REAL NOT NULL,
    data_quality_status VARCHAR(20) DEFAULT 'CLEAN',
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES dim_sensors(sensor_id)
);

INSERT OR IGNORE INTO dim_facilities VALUES 
('FAC01', 'Pune Processing Plant', 'Asia-Pacific', 1),
('FAC02', 'Nashik Purification Unit', 'Asia-Pacific', 1),
('FAC03', 'Navi Mumbai Hub', 'Asia-Pacific', 1);

INSERT OR IGNORE INTO dim_sensors VALUES 
('SEN-WTR-01', 'FAC01', 'Water Flow Meter', 'L/min'),
('SEN-CHM-02', 'FAC02', 'Chemical Dosing', 'ppm'),
('SEN-ENG-03', 'FAC03', 'Energy Consumption', 'kWh');
