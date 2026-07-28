import pandas as pd
import numpy as np
import os
from rapidfuzz import process, fuzz


# PATH SETUP
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_path = os.path.join(BASE_DIR, "data", "raw", "ev_market_raw.csv")
output_path = os.path.join(BASE_DIR, "data", "cleaned", "ev_market_cleaned.csv")

try:

    # LOAD DATA
    df = pd.read_csv(input_path)


    # COLUMN STANDARDIZATION
    df.columns = df.columns.str.strip().str.lower()
    df = df.drop_duplicates()


    # SCHEMA VALIDATION

    required_cols = [
        'price_inr','units_sold','battery_kwh',
        'range_km','charging_time','sales_date'
    ]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")


    # NUMERIC CLEANING

    num_cols = ['price_inr', 'units_sold', 'battery_kwh', 'range_km', 'charging_time']

    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        median_val = df[col].median()

        df[col] = df[col].fillna(median_val)
        df[col] = df[col].replace(0, median_val)
        df[col] = df[col].abs()


    # OUTLIER HANDLING

    for col in num_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR

        df[col] = np.clip(df[col], lower, upper)


    # LOGICAL VALIDATION

    df = df[df['battery_kwh'] > 0]
    df = df[df['range_km'] > 0]


    # TEXT STANDARDIZATION

    categorical_cols = ['segment', 'usage_type', 'customer_type', 'area_type']
    fuzzy_cols = ['manufacturer', 'model', 'city']
    text_cols = categorical_cols + fuzzy_cols

    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()
            df[col] = df[col].replace({'Nan': np.nan, 'None': np.nan})
            df[col] = df[col].fillna('Unknown')


    # FUZZY MATCHING 

    fuzzy_thresholds = {
        'manufacturer': 65,
        'city': 65,
        'model': 85
    }

    for col in fuzzy_cols:
        if col in df.columns:
            freq = df[col].value_counts()
            min_count = max(3, int(len(df) * 0.01))
            valid_words = freq[freq >= min_count].index.tolist()
            all_words = freq.index.tolist()

            threshold = fuzzy_thresholds.get(col, 85)
            mapping = {}

            for word in all_words:
                if word == 'Unknown' or word in valid_words:
                    continue

                match = process.extractOne(word, valid_words, scorer=fuzz.token_sort_ratio)

                if match:
                    best_match, score, _ = match

                    if score >= threshold and best_match != word:
                        mapping[word] = best_match

            df[col] = df[col].replace(mapping)


    # DATE CLEANING

    df['sales_date'] = pd.to_datetime(
    df['sales_date'],
    dayfirst=True,
    errors='coerce'
)
    df = df.dropna(subset=['sales_date'])


    # FEATURE ENGINEERING

    df['revenue'] = df['price_inr'] * df['units_sold']

    df['efficiency'] = np.where(
        df['battery_kwh'] > 0,
        round(df['range_km'] / df['battery_kwh'], 2),
        0
    )

    df['charging_type'] = df['charging_time'].apply(
        lambda x: 'Fast Charging' if x <= 6 else 'Slow Charging'
    )



    # FINAL CLEANUP

    df.reset_index(drop=True, inplace=True)


    # EXPORT CLEAN DATA

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print("Cleaning completed successfully")
    print(f"Final Shape: {df.shape}")
    print(f"Total Null Values: {df.isnull().sum().sum()}")
    print("\nFIRST 5 ROWS:")
    print(df.head())
    
except Exception as e:
    print(f"Pipeline failed: {str(e)}")