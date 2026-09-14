import os

# Create folders
for d in ['data', 'sql', 'src', 'docs']:
    os.makedirs(d, exist_ok=True)

# requirements.txt
with open('requirements.txt', 'w') as f:
    f.write('pandas\ntabulate\n')

# data/raw_telemetry.csv
csv_data = '''facility_id,sensor_id,sensor_type,reading_timestamp,reading_value,unit_of_measure
FAC01,SEN-WTR-01,Water Flow Meter,2026-09-10 08:00:00,120.5,L/min
FAC01,SEN-WTR-01,Water Flow Meter,2026-09-10 08:00:00,120.5,L/min
FAC01,SEN-WTR-01,Water Flow Meter,2026-09-10 08:15:00,124.0,L/min
FAC01,SEN-WTR-01,Water Flow Meter,2026-09-10 08:30:00,,L/min
FAC01,SEN-WTR-01,Water Flow Meter,2026-09-10 08:45:00,-99.0,L/min
FAC01,SEN-WTR-01,Water Flow Meter,2026-09-10 09:00:00,210.0,L/min
FAC02,SEN-CHM-02,Chemical Dosing,2026-09-10 08:00:00,15.2,ppm
FAC02,SEN-CHM-02,Chemical Dosing,bad_timestamp,15.8,ppm
FAC02,SEN-CHM-02,Chemical Dosing,2026-09-10 08:30:00,16.1,ppm
FAC02,SEN-CHM-02,Chemical Dosing,2026-09-10 08:45:00,55.0,ppm
FAC03,SEN-ENG-03,Energy Consumption,2026-09-10 08:00:00,340.2,kWh
FAC03,SEN-ENG-03,Energy Consumption,2026-09-10 08:15:00,342.0,kWh
'''
with open('data/raw_telemetry.csv', 'w') as f:
    f.write(csv_data)

# sql/01_schema.sql
schema_sql = '''CREATE TABLE IF NOT EXISTS dim_facilities (
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
'''
with open('sql/01_schema.sql', 'w') as f:
    f.write(schema_sql)

# src/etl_pipeline.py
etl_code = '''import sqlite3
import pandas as pd

DB_FILE = 'enterprise_telemetry.db'
CSV_PATH = 'data/raw_telemetry.csv'
SCHEMA_PATH = 'sql/01_schema.sql'

def run_pipeline():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    with open(SCHEMA_PATH, 'r') as f:
        cursor.executescript(f.read())
    print('[ETL STEP 1] Database relational schema initialized.')

    df_raw = pd.read_csv(CSV_PATH)
    initial_rows = len(df_raw)
    print(f'[ETL STEP 2] Raw extraction: {initial_rows} records ingested.')

    df_clean = df_raw.dropna(subset=['reading_value']).copy()
    df_clean['reading_timestamp'] = pd.to_datetime(df_clean['reading_timestamp'], errors='coerce')
    df_clean = df_clean.dropna(subset=['reading_timestamp'])
    df_clean = df_clean[df_clean['reading_value'] >= 0]
    df_clean = df_clean.drop_duplicates(subset=['sensor_id', 'reading_timestamp'])

    payload = df_clean[['sensor_id', 'reading_timestamp', 'reading_value']]
    records_transformed = len(payload)
    print(f'[ETL STEP 3] Cleaned: {initial_rows - records_transformed} dirty rows dropped.')

    payload.to_sql('fact_telemetry_readings', conn, if_exists='append', index=False)
    conn.commit()
    conn.close()
    print(f'[ETL STEP 4] Load: {records_transformed} validated rows inserted.')

if __name__ == '__main__':
    run_pipeline()
'''
with open('src/etl_pipeline.py', 'w') as f:
    f.write(etl_code)

# src/data_quality_checks.py
dq_code = '''import sqlite3

def execute_data_audits():
    conn = sqlite3.connect('enterprise_telemetry.db')
    cursor = conn.cursor()

    audit_rules = {
        'Rule 1: Null Value Assertion': 'SELECT COUNT(*) FROM fact_telemetry_readings WHERE reading_value IS NULL;',
        'Rule 2: Foreign Key Referential Integrity': 'SELECT COUNT(*) FROM fact_telemetry_readings t LEFT JOIN dim_sensors s ON t.sensor_id = s.sensor_id WHERE s.sensor_id IS NULL;',
        'Rule 3: Duplicate Natural Key Check': 'SELECT COUNT(*) FROM (SELECT sensor_id, reading_timestamp, COUNT(*) FROM fact_telemetry_readings GROUP BY sensor_id, reading_timestamp HAVING COUNT(*) > 1);',
        'Rule 4: Domain Range Boundary Check': 'SELECT COUNT(*) FROM fact_telemetry_readings WHERE reading_value < 0;'
    }

    print('\\n=======================================================')
    print('      ENTERPRISE DATA QUALITY AUDIT & GOVERNANCE       ')
    print('=======================================================')

    for test_name, query in audit_rules.items():
        failures = cursor.execute(query).fetchone()[0]
        status = 'PASSED' if failures == 0 else f'FAILED ({failures} violations)'
        print(f'[{status}] {test_name}')

    print('=======================================================\\n')
    conn.close()

if __name__ == '__main__':
    execute_data_audits()
'''
with open('src/data_quality_checks.py', 'w') as f:
    f.write(dq_code)

# sql/02_analytics_queries.sql
sql_queries = '''-- Relational Joins & Aggregations
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
'''
with open('sql/02_analytics_queries.sql', 'w') as f:
    f.write(sql_queries)

# docs/data_governance_dictionary.md
gov_text = '''# Enterprise Telemetry Data Governance & Security Catalog

## 1. System Architecture & Entity Relationships
The data system implements a Star-Schema dimensional architecture:
* dim_facilities (Primary Dimension)
* dim_sensors (Dimension)
* fact_telemetry_readings (Fact Table)

## 2. Governance & Data Security
* facility_id: VARCHAR(10), Internal
* operating_region: VARCHAR(50), Confidential (Masked)
* reading_value: REAL, Operational Critical (Non-negative check)
* reading_timestamp: TIMESTAMP, Operational (ISO-8601 deduplicated)
'''
with open('docs/data_governance_dictionary.md', 'w') as f:
    f.write(gov_text)

# README.md
readme_text = '''# Enterprise Facility Telemetry Pipeline & Data Quality Auditor
End-to-end ELT, Relational Database Modeling, and Data Quality Framework for industrial monitoring.
'''
with open('README.md', 'w') as f:
    f.write(readme_text)

print('SUCCESS: All files and keywords generated!')
