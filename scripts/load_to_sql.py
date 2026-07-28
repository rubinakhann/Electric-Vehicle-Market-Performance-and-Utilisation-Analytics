#LOAD TO SQL 
import sqlite3
import pandas as pd
import os

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, "ev_analytics.db")
CLEANED_FILE = os.path.join(BASE_DIR, "data", "cleaned", "ev_market_cleaned.csv")

if not os.path.exists(CLEANED_FILE):
    print(f"Error: Cleaned file not found at {CLEANED_FILE}")
else:
    # Load cleaned data
    df = pd.read_csv(CLEANED_FILE)
    df['sales_date'] = pd.to_datetime(df['sales_date'], errors='coerce')
    df = df.dropna(subset=['sales_date'])

    # Connect to SQLite
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Drop existing tables
    cursor.executescript("""
    DROP TABLE IF EXISTS fact_ev_sales;
    DROP TABLE IF EXISTS dim_vehicle;
    DROP TABLE IF EXISTS dim_location;
    DROP TABLE IF EXISTS dim_segment;
    DROP TABLE IF EXISTS dim_usage;
    """)

    # 1. Dim Vehicle 
    dim_vehicle = df[['vehicle_id', 'manufacturer', 'model', 'battery_kwh', 
                      'range_km', 'charging_time', 'charging_type','efficiency']].drop_duplicates()
    dim_vehicle.to_sql("dim_vehicle", conn, index=False, if_exists='replace')

    # 2. Dim Location 
    dim_location = df[['city', 'area_type']].drop_duplicates().reset_index(drop=True)
    dim_location['location_id'] = dim_location.index + 1
    dim_location.to_sql("dim_location", conn, index=False, if_exists='replace')

    # 3. Dim Segment
    dim_segment = df[['segment']].drop_duplicates().reset_index(drop=True)
    dim_segment['segment_id'] = dim_segment.index + 1
    dim_segment.to_sql("dim_segment", conn, index=False, if_exists='replace')

    # 4. Dim Usage 
    dim_usage = df[['usage_type', 'customer_type']].drop_duplicates().reset_index(drop=True)
    dim_usage['usage_id'] = dim_usage.index + 1
    dim_usage.to_sql('dim_usage', conn, index=False, if_exists='replace')

    # 5. Fact Table 
    df = df.merge(dim_location, on=['city', 'area_type'], how='left')
    df = df.merge(dim_segment, on='segment', how='left')
    df = df.merge(dim_usage, on=['usage_type', 'customer_type'], how='left')

    # Final Fact Table with all metrics
    fact = df[['vehicle_id', 'location_id', 'segment_id', 'usage_id', 
              'units_sold', 'price_inr', 'revenue', 'sales_date']]
    
    fact.to_sql("fact_ev_sales", conn, index=False, if_exists='replace')

    conn.commit()
    conn.close()
    
    print(f"---EV Database Loaded Successfully ---")
    print(f"Location: {DB_FILE}")
