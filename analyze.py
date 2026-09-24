"""
Exploratory data inspection utility for the FreightTiger case study.

This script performs lightweight exploratory analysis on input datasets and output contracts.
The production pipeline is implemented in src/ and executed through run_pipeline.py.
"""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

shipment_path = DATA_DIR / "shipment_records.csv"
notes_path = DATA_DIR / "context_notes.csv"
sample_out_path = DATA_DIR / "sample_output_format_v2.csv"

df_ship = pd.read_csv(shipment_path)
df_notes = pd.read_csv(notes_path)

print("=== 1. SHIPMENT DATASET ANALYSIS ===")
print("Columns:", list(df_ship.columns))
print("Data Types:\n", df_ship.dtypes)
print("Row Count:", len(df_ship))
print("Missing Values:\n", df_ship.isnull().sum())
print("Date Range:", df_ship['shipment_date'].min(), "to", df_ship['shipment_date'].max())

# Create route column
df_ship['route'] = df_ship['origin'] + "-" + df_ship['destination']
print("Unique Routes:", df_ship['route'].unique())
print("Route Count:", df_ship['route'].nunique())

route_by_type = df_ship.groupby('route_type')['route'].unique()
print("Route Types and Routes:")
for rtype, routes in route_by_type.items():
    print(f"  {rtype}: {routes}")

# Week range calculation
df_ship['dt'] = pd.to_datetime(df_ship['shipment_date'])
df_ship['week_of'] = df_ship['dt'].apply(lambda d: d - pd.Timedelta(days=d.weekday()))
print("Min Monday week_of:", df_ship['week_of'].min().strftime('%Y-%m-%d'))
print("Max Monday week_of:", df_ship['week_of'].max().strftime('%Y-%m-%d'))
print("Total distinct weeks:", df_ship['week_of'].nunique())

print("\n=== 2. CONTEXT NOTES ANALYSIS ===")
print("Columns:", list(df_notes.columns))
print("Note IDs:", df_notes['note_id'].tolist())
for idx, row in df_notes.iterrows():
    print(f"Note {row['note_id']} | Date: {row['date']} | Applies To: {row['applies_to']}")
    print(f"   Text: {row['note']}")

print("\n=== 3. OUTPUT CONTRACT ANALYSIS ===")
try:
    df_sample = pd.read_csv(sample_out_path)
    print("Sample Columns:", list(df_sample.columns))
    print("Sample Shape:", df_sample.shape)
    print("Sample Data:\n", df_sample)
except Exception:
    with open(sample_out_path, "r", encoding="utf-8") as f:
        sample_content = f.read()
    print(f"Sample File Path: {sample_out_path}")
    print("Sample Output Raw Content:\n", sample_content.strip())


