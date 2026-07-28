#KPI SCRIPT
import sqlite3
import os
import pandas as pd

# --- Path Setup ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, "ev_analytics.db")
# Connect to SQL Database
conn = sqlite3.connect(DB_FILE)
print(" Connected to Database Successfully")

# --- KPI 1: TOTAL SALES ---
kpi1 = pd.read_sql("SELECT SUM(units_sold) AS total_units FROM fact_ev_sales;", conn)
print(" Total EV Units Sold:\n", kpi1, "\n")

# --- KPI 2: TOTAL REVENUE ---
kpi2 = pd.read_sql("SELECT SUM(revenue) AS total_revenue FROM fact_ev_sales;", conn)
print(" Total Revenue:\n", kpi2, "\n")

# --- KPI 3: AVERAGE PRICE ---
kpi3 = pd.read_sql("SELECT ROUND(AVG(price_inr),2) AS avg_price FROM fact_ev_sales;", conn)
print(" Average Price:\n", kpi3, "\n")

# --- KPI 4: TOP MANUFACTURER ---
kpi4 = pd.read_sql("""
    SELECT v.manufacturer, SUM(f.units_sold) AS total_units
    FROM fact_ev_sales f
    JOIN dim_vehicle v ON f.vehicle_id = v.vehicle_id
    GROUP BY v.manufacturer
    ORDER BY total_units DESC LIMIT 1;
""", conn)
print(" Top Manufacturer:\n", kpi4, "\n")

# --- KPI 5: MARKET SHARE ---
kpi5 = pd.read_sql("""
    SELECT v.manufacturer,
           SUM(f.units_sold) AS total_units,
           ROUND(100.0 * SUM(f.units_sold) / (SELECT SUM(units_sold) FROM fact_ev_sales), 2) AS market_share_pct
    FROM fact_ev_sales f
    JOIN dim_vehicle v ON f.vehicle_id = v.vehicle_id
    GROUP BY v.manufacturer
    ORDER BY total_units DESC;
""", conn)
print(" Manufacturer Market Share:\n", kpi5, "\n")

# --- KPI 6: SEGMENT SALES ---
kpi6 = pd.read_sql("""
    SELECT s.segment, SUM(f.units_sold) AS total_units
    FROM fact_ev_sales f
    JOIN dim_segment s ON f.segment_id = s.segment_id
    GROUP BY s.segment
    ORDER BY total_units DESC;
""", conn)
print(" Segment-wise Sales:\n", kpi6, "\n")

# --- KPI 7: TOP 5 CITIES ---
kpi7 = pd.read_sql("""
    SELECT l.city, SUM(f.revenue) AS total_revenue
    FROM fact_ev_sales f
    JOIN dim_location l ON f.location_id = l.location_id
    GROUP BY l.city
    ORDER BY total_revenue DESC LIMIT 5;
""", conn)
print(" Top 5 Cities by Revenue:\n", kpi7, "\n")

# --- KPI 8: AVG BATTERY EFFICIENCY ---
kpi9 = pd.read_sql("SELECT ROUND(AVG(efficiency),2) AS avg_efficiency FROM dim_vehicle;", conn)
print(" Avg Battery Efficiency:\n", kpi9, "\n")

# --- KPI 9: YEAR-WISE SALES ---
kpi10 = pd.read_sql("""
    SELECT STRFTIME('%Y', sales_date) AS year, SUM(units_sold) AS total_units
    FROM fact_ev_sales
    GROUP BY year ORDER BY year;
""", conn)
print(" Year-wise Sales:\n", kpi10, "\n")

# --- KPI 10: TOP MODELS ---
kpi11 = pd.read_sql("""
    SELECT v.model, SUM(f.units_sold) AS total_units
    FROM fact_ev_sales f
    JOIN dim_vehicle v ON f.vehicle_id = v.vehicle_id
    GROUP BY v.model
    ORDER BY total_units DESC LIMIT 5;
""", conn)
print(" Top 5 Models:\n", kpi11, "\n")

# --- KPI 11: SEGMENT RECORD COUNT ---
kpi12 = pd.read_sql("""
    SELECT s.segment, COUNT(*) AS record_count
    FROM fact_ev_sales f
    JOIN dim_segment s ON f.segment_id = s.segment_id
    GROUP BY s.segment;
""", conn)
print(" Segment-wise Record Count:\n", kpi12, "\n")

# Close Database Connection
conn.close()
print(" KPI ANALYSIS COMPLETED SUCCESSFULLY")