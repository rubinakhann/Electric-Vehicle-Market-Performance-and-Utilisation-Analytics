import subprocess
import sys

print("EV Market Pipeline Started")

try:
    print("\n[Step 0]: Initial EDA started (Raw Data Audit)")
    subprocess.run([sys.executable, "scripts/initial_eda.py"], check=True)

    print("\n[Step 1]: Data Cleaning started")
    subprocess.run([sys.executable, "scripts/data_cleaning.py"], check=True)

    print("\n[Step 2]: Loading data to SQLite database")
    subprocess.run([sys.executable, "scripts/load_to_sql.py"], check=True)

    print("\n[Step 3]: KPI Calculation started")
    subprocess.run([sys.executable, "scripts/kpi_run.py"], check=True)

    print("PIPELINE COMPLETED SUCCESSFULLY!")
    
except Exception as e:
    print("\n failed!")
    print(e)
