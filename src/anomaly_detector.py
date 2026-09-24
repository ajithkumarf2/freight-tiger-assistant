"""
Step 3: Deterministic Anomaly Candidate Detection Engine.

Evaluates weekly route metrics against the configured ANOMALY_THRESHOLD to detect
candidate anomalies. This step is strictly deterministic and does NOT read context notes
or use LLMs/RAG.
"""

import pandas as pd
import numpy as np
from src.config import ANOMALY_THRESHOLD


def detect_anomaly_candidates(metrics_df: pd.DataFrame) -> pd.DataFrame:
    """
    Evaluates each route-week in metrics_df to determine if it is an anomaly candidate.

    Rule:
    is_anomaly_candidate = True if (vs_own_history_pct >= ANOMALY_THRESHOLD)
                                OR (vs_similar_routes_pct >= ANOMALY_THRESHOLD)

    Only positive/rising deviations qualify.
    NaN values do not qualify by themselves (comparison with NaN evaluates to False).

    Args:
        metrics_df (pd.DataFrame): DataFrame containing 'vs_own_history_pct'
                                   and 'vs_similar_routes_pct'.

    Returns:
        pd.DataFrame: Copy of metrics_df with added boolean column 'is_anomaly_candidate'.
    """
    df = metrics_df.copy()

    # Compare against ANOMALY_THRESHOLD imported from config
    # In Python/pandas, x >= threshold evaluates to False for NaN values
    own_qualifies = (df['vs_own_history_pct'].notnull()) & (df['vs_own_history_pct'] >= ANOMALY_THRESHOLD)
    peer_qualifies = (df['vs_similar_routes_pct'].notnull()) & (df['vs_similar_routes_pct'] >= ANOMALY_THRESHOLD)

    df['is_anomaly_candidate'] = (own_qualifies | peer_qualifies).astype(bool)

    return df
