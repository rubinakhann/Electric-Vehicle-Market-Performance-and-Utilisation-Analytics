import os
import pandas as pd

# Path Setup 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FILE = os.path.join(BASE_DIR, "data", "raw", "ev_market_raw.csv")

print("INITIAL EDA STARTED")

if not os.path.exists(RAW_FILE):
    print(f"Error: raw data file not found at {RAW_FILE}")
    print("Please check your data/raw directory structure!")
else:
    # Load Raw Data
    df = pd.read_csv(RAW_FILE)
    
    
    if 'sales_date' in df.columns:
        df['sales_date'] = pd.to_datetime(df['sales_date'], format='%d-%m-%Y', errors='coerce')

    # 1. Structural Audit
    print("--- 1. DATA STRUCTURE & FORMATS ---")
    print(f"Dimensions: {df.shape[0]} rows | {df.shape[1]} columns")
    print(f"Total Duplicate Rows: {df.duplicated().sum()}")
    if 'vehicle_id' in df.columns:
        print(f"Duplicate Vehicle IDs: {df['vehicle_id'].duplicated().sum()}")
    print("\nColumn Data Types:")
    print(df.dtypes)
    print("-" * 50)

    # 2. Complete Column Missing/Null Scan
    print("--- 2. COLUMN MISSING VALUES SCAN ---")
    print(df.isnull().sum())
    print("-" * 50)

    # 3. Categorical Column Unique Value & Text Error Scan
    print("--- 3. CATEGORICAL UNIQUE COUNTS & CARDINALITY ---")
    cat_cols = ['manufacturer', 'model', 'segment', 'usage_type', 'customer_type', 'area_type', 'city', 'charging_type']
    for col in cat_cols:
        if col in df.columns:
            print(f"Column [{col}]: Unique Values Count = {df[col].nunique()}")
            print(f"Top 3 Values:\n{df[col].value_counts().head(3)}")
            print()
    print("-" * 50)

    # 4. Numerical Fields Range and Outlier Detection
    print("--- 4. NUMERICAL LOGICAL CHECKS & RANGES ---")
    num_cols = ['price_inr', 'units_sold', 'battery_kwh', 'range_km', 'revenue', 'efficiency']
    for col in num_cols:
        if col in df.columns:
            print(f"Column [{col}]:")
            print(f"  - Zeros: {(df[col] == 0).sum()} | Negatives: {(df[col] < 0).sum()}")
            print(f"  - Range: Min = {df[col].min()} | Median = {df[col].median()} | Max = {df[col].max()}")
    print("-" * 50)

    # 5. Date Field Logic Check
    print("--- 5. TEMPORAL BOUNDARY CHECK ---")
    if 'sales_date' in df.columns:
        valid_dates = df['sales_date'].dropna()
        if not valid_dates.empty:
            print(f"Date Range Cover: From {valid_dates.min().date()} To {valid_dates.max().date()}")
    
    print("INITIAL EDA COMPLETED SUCCESSFULLY")