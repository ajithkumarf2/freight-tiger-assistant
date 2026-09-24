"""
Data loading compatibility wrapper for FreightTiger Shipping Cost Assistant.
"""

from src.context_notes import load_context_notes
import pandas as pd


def load_shipment_records(csv_path: str = "data/shipment_records.csv") -> pd.DataFrame:
    """Loads shipment_records.csv into a pandas DataFrame."""
    return pd.read_csv(csv_path)
