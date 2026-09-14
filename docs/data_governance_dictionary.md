# Enterprise Telemetry Data Governance & Security Catalog

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
