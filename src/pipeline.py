import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime

class TelemetryPipeline:
    def __init__(self, db_path: str = "enterprise_telemetry.db"):
        self.db_path = db_path

    def ingest_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sanitizes raw telemetry payload, strips nulls and verifies datatypes."""
        clean_df = df.dropna(subset=['facility_id', 'metric_value']).copy()
        clean_df['metric_value'] = pd.to_numeric(clean_df['metric_value'], errors='coerce')
        clean_df = clean_df.dropna(subset=['metric_value'])
        
        if 'recorded_timestamp' not in clean_df.columns or clean_df['recorded_timestamp'].isnull().all():
            clean_df['recorded_timestamp'] = datetime.utcnow().isoformat()
        else:
            clean_df['recorded_timestamp'] = pd.to_datetime(clean_df['recorded_timestamp']).dt.strftime('%Y-%m-%dT%H:%M:%S')
            
        return clean_df

    def detect_anomalies(self, df: pd.DataFrame, threshold_std: float = 2.0) -> pd.DataFrame:
        """Statistical outlier flagger via Rolling / Global Z-Score deviation."""
        evaluated_df = df.copy()
        mean = evaluated_df['metric_value'].mean()
        std = evaluated_df['metric_value'].std()
        
        if pd.isna(std) or std == 0:
            evaluated_df['anomaly_flag'] = 0
            evaluated_df['z_score'] = 0.0
        else:
            evaluated_df['z_score'] = (evaluated_df['metric_value'] - mean) / std
            evaluated_df['anomaly_flag'] = evaluated_df['z_score'].abs().apply(lambda x: 1 if x >= threshold_std else 0)
            
        return evaluated_df

    def load_to_database(self, df: pd.DataFrame, table_name: str = "telemetry_records"):
        """Atomic batch insertion into SQLite transactional datamart."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    facility_id TEXT NOT NULL,
                    recorded_timestamp TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    z_score REAL,
                    anomaly_flag INTEGER NOT NULL
                )
            """)
            
            records = df[['facility_id', 'recorded_timestamp', 'metric_value', 'z_score', 'anomaly_flag']].to_records(index=False)
            cursor.executemany(f"""
                INSERT INTO {table_name} (facility_id, recorded_timestamp, metric_value, z_score, anomaly_flag)
                VALUES (?, ?, ?, ?, ?)
            """, list(records))
            conn.commit()

    def run_pipeline(self, df: pd.DataFrame):
        cleaned = self.ingest_and_clean(df)
        analyzed = self.detect_anomalies(cleaned)
        self.load_to_database(analyzed)
        return analyzed
