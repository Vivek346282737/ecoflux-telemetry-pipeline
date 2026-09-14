# Enterprise Facility Telemetry Pipeline & Data Quality Auditor

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-lightgrey?logo=sqlite)](https://www.sqlite.org/)
[![Data-Quality](https://img.shields.io/badge/Data%20Quality-Audited%20%26%20Enforced-brightgreen)](#2-automated-data-quality--integrity-audits)
[![Data-Modeling](https://img.shields.io/badge/Architecture-Star--Schema-orange)](#architecture--system-relationships)

An enterprise-grade ELT (Extract-Load-Transform) telemetry processing system designed for industrial utility and asset resource tracking (water flow, chemical dosing, energy consumption).

This pipeline ingests streaming IoT operational metrics, executes automated data cleaning, enforces referential integrity across relational entities, performs validation assertions, and generates SQL analytics for operational anomaly detection.

---

## Architecture & System Relationships

The data layer implements a normalized **Star-Schema Relational Model** ensuring ACID compliance and referential integrity:

---

## Live Verification & Execution Logs (Proof of Implementation)

### 1. Data Quality Suite Audit Log
\\	ext
=======================================================
      ENTERPRISE DATA QUALITY AUDIT & GOVERNANCE       
=======================================================
[PASSED] Rule 1: Null Value Assertion in Core Metric
[PASSED] Rule 2: Foreign Key Referential Integrity (Orphan Sensors)
[PASSED] Rule 3: Duplicate Natural Key Check
[PASSED] Rule 4: Domain Range Boundary Check
-------------------------------------------------------
AUDIT RESULT: ALL CHECKS HEALTHY
=======================================================
\
### 2. SQL Analytics Engine Query Results
\\	ext
--- FACILITY TELEMETRY CONSUMPTION SUMMARY ---
           facility_name operating_region        sensor_type  total_readings  avg_consumption unit_of_measure
Nashik Purification Unit     Asia-Pacific    Chemical Dosing               3            28.77             ppm
         Navi Mumbai Hub     Asia-Pacific Energy Consumption               2           341.10             kWh
   Pune Processing Plant     Asia-Pacific   Water Flow Meter               3           151.50           L/min

--- ANOMALY SPIKE DETECTION (WINDOW FUNCTION LAG) ---
 sensor_id   reading_timestamp  previous_reading  current_reading  pct_surge
SEN-CHM-02 2026-09-10 08:45:00              16.1             55.0     241.61%
SEN-WTR-01 2026-09-10 09:00:00             124.0            210.0      69.35%
\