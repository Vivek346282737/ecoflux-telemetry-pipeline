import sqlite3
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
