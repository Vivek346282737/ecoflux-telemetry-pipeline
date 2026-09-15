import pandas as pd
from src.pipeline import TelemetryPipeline

if __name__ == "__main__":
    print("[INIT]: Loading raw batch telemetry data...")
    df = pd.read_csv("data/sample_telemetry.csv")
    pipeline = TelemetryPipeline("enterprise_telemetry.db")
    results = pipeline.run_pipeline(df)
    print("[SUCCESS]: Telemetry processed and loaded into SQLite datamart.")
    print(results[['facility_id', 'recorded_timestamp', 'metric_value', 'anomaly_flag']])
