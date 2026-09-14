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