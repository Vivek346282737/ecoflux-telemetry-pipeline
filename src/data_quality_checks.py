import sqlite3

def execute_data_audits():
    conn = sqlite3.connect('enterprise_telemetry.db')
    cursor = conn.cursor()

    audit_rules = {
        'Rule 1: Null Value Assertion': 'SELECT COUNT(*) FROM fact_telemetry_readings WHERE reading_value IS NULL;',
        'Rule 2: Foreign Key Referential Integrity': 'SELECT COUNT(*) FROM fact_telemetry_readings t LEFT JOIN dim_sensors s ON t.sensor_id = s.sensor_id WHERE s.sensor_id IS NULL;',
        'Rule 3: Duplicate Natural Key Check': 'SELECT COUNT(*) FROM (SELECT sensor_id, reading_timestamp, COUNT(*) FROM fact_telemetry_readings GROUP BY sensor_id, reading_timestamp HAVING COUNT(*) > 1);',
        'Rule 4: Domain Range Boundary Check': 'SELECT COUNT(*) FROM fact_telemetry_readings WHERE reading_value < 0;'
    }

    print('\n=======================================================')
    print('      ENTERPRISE DATA QUALITY AUDIT & GOVERNANCE       ')
    print('=======================================================')

    for test_name, query in audit_rules.items():
        failures = cursor.execute(query).fetchone()[0]
        status = 'PASSED' if failures == 0 else f'FAILED ({failures} violations)'
        print(f'[{status}] {test_name}')

    print('=======================================================\n')
    conn.close()

if __name__ == '__main__':
    execute_data_audits()
