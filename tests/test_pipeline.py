import pytest
import pandas as pd
import sqlite3
import os
from src.pipeline import TelemetryPipeline

@pytest.fixture
def temp_db(tmp_path):
    return str(tmp_path / "test_telemetry.db")

def test_pipeline_cleaning():
    pipeline = TelemetryPipeline(":memory:")
    raw_data = pd.DataFrame({
        'facility_id': ['FAC_01', None, 'FAC_02', 'FAC_03'],
        'metric_value': [104.5, 99.1, 'invalid_num', 120.0],
        'recorded_timestamp': ['2026-09-15 10:00:00', '2026-09-15 10:05:00', '2026-09-15 10:10:00', None]
    })
    cleaned = pipeline.ingest_and_clean(raw_data)
    assert len(cleaned) == 2
    assert set(cleaned['facility_id']) == {'FAC_01', 'FAC_03'}

def test_pipeline_anomaly_detection():
    pipeline = TelemetryPipeline(":memory:")
    data = pd.DataFrame({
        'facility_id': ['FAC_A'] * 6,
        'metric_value': [10.0, 10.2, 9.8, 10.1, 10.0, 95.0],
        'recorded_timestamp': ['2026-09-15 12:00:00'] * 6
    })
    result = pipeline.detect_anomalies(data, threshold_std=2.0)
    assert result['anomaly_flag'].sum() == 1
    assert result.iloc[-1]['anomaly_flag'] == 1

def test_pipeline_database_load(temp_db):
    pipeline = TelemetryPipeline(temp_db)
    data = pd.DataFrame({
        'facility_id': ['FAC_NORTH', 'FAC_SOUTH'],
        'metric_value': [45.2, 51.8],
        'recorded_timestamp': ['2026-09-15 14:00:00', '2026-09-15 14:05:00']
    })
    pipeline.run_pipeline(data)
    
    with sqlite3.connect(temp_db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM telemetry_records")
        count = cursor.fetchone()[0]
    assert count == 2
