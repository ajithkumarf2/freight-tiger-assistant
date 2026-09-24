"""
Step 6: Output Generator Engine for FreightTiger Shipping Cost Assistant.

Formats and exports the final CSV output matching sample_output_format_v2.csv exactly.
Deterministic field ownership is strictly preserved:
- route, week_of, cost_per_tonne_km, vs_own_history, vs_similar_routes, flagged, matched_note_id
  come from deterministic calculation and evidence validation steps.
- reason comes from grounded Step 5 LLM explanation (or deterministic fallback).
"""

import os
import csv
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

# Exact column schema and order required by FreightTiger output contract
EXPECTED_COLUMNS = [
    "route",
    "week_of",
    "cost_per_tonne_km",
    "vs_own_history",
    "vs_similar_routes",
    "flagged",
    "matched_note_id",
    "reason"
]


def format_percentage_own_history(val: float) -> str:
    """Formats vs_own_history_pct into '+X.X% vs this route\'s past average'."""
    if pd.isnull(val):
        return "N/A"
    pct_val = val * 100.0
    return f"{pct_val:+.1f}% vs this route's past average"


def format_percentage_similar_routes(val: float) -> str:
    """Formats vs_similar_routes_pct into '+X.X% vs similar-length routes this week'."""
    if pd.isnull(val):
        return "N/A"
    pct_val = val * 100.0
    return f"{pct_val:+.1f}% vs similar-length routes this week"


def format_cost_per_tonne_km(val: float) -> str:
    """Rounds cost_per_tonne_km to exactly 2 decimal places."""
    if pd.isnull(val):
        return "0.00"
    return f"{val:.2f}"


def format_final_output(
    candidate_df: pd.DataFrame,
    explanation_results: List[Dict[str, Any]]
) -> pd.DataFrame:
    """
    Constructs the final formatted output DataFrame containing ONLY anomaly candidates.

    Args:
        candidate_df (pd.DataFrame): DataFrame containing weekly metrics and 'is_anomaly_candidate'.
        explanation_results (List[Dict[str, Any]]): List of dicts from Step 4 & 5 containing
                                                      validated evidence and LLM reasons.

    Returns:
        pd.DataFrame: Formatted DataFrame matching the 8 required contract columns.
    """
    # Filter ONLY anomaly candidates
    if 'is_anomaly_candidate' in candidate_df.columns:
        filtered_df = candidate_df[candidate_df['is_anomaly_candidate'] == True].copy()
    else:
        filtered_df = candidate_df.copy()

    # Create lookup map for LLM reasons and validated note IDs from Step 4/5
    exp_map: Dict[tuple, Dict[str, Any]] = {}
    for item in explanation_results:
        key = (str(item.get("route")), str(item.get("week_of")))
        exp_map[key] = item

    formatted_rows = []
    for idx, row in filtered_df.iterrows():
        route = str(row["route"])
        week_of = str(row["week_of"])
        key = (route, week_of)
        exp_data = exp_map.get(key, {})

        # 1. Deterministic cost_per_tonne_km (2 decimal places)
        cptk_str = format_cost_per_tonne_km(row["cost_per_tonne_km"])

        # 2. Deterministic percentage strings (1 decimal place)
        vs_own_str = format_percentage_own_history(row["vs_own_history_pct"])
        vs_similar_str = format_percentage_similar_routes(row["vs_similar_routes_pct"])

        # 3. Deterministic matched_note_id & flagged value from Step 4
        matched_note_id = exp_data.get("validated_note_id", "")
        if matched_note_id is None:
            matched_note_id = ""

        # Flagged logic: "No (justified)" if valid evidence exists, else "Yes"
        if matched_note_id != "":
            flagged_str = "No (justified)"
        else:
            flagged_str = "Yes"

        # 4. Reason field from Step 5 LLM or deterministic fallback
        reason_str = exp_data.get("reason", "")
        if not reason_str:
            if matched_note_id != "":
                reason_str = f"Matches note {matched_note_id}: cost rise has a clear explanation."
            else:
                reason_str = "No valid supporting note was found for this route or date range. Cost rise looks unexplained and worth a human review."

        output_row = {
            "route": route,
            "week_of": week_of,
            "cost_per_tonne_km": cptk_str,
            "vs_own_history": vs_own_str,
            "vs_similar_routes": vs_similar_str,
            "flagged": flagged_str,
            "matched_note_id": matched_note_id,
            "reason": reason_str
        }
        formatted_rows.append(output_row)

    out_df = pd.DataFrame(formatted_rows)
    
    # Ensure exact column ordering
    if not out_df.empty:
        out_df = out_df[EXPECTED_COLUMNS]
    else:
        out_df = pd.DataFrame(columns=EXPECTED_COLUMNS)

    return out_df


def save_final_csv(
    output_df: pd.DataFrame,
    output_path: Optional[str] = None
) -> str:
    """
    Saves the final output DataFrame to CSV with proper quoting to preserve commas in reason fields.

    Args:
        output_df (pd.DataFrame): Formatted DataFrame.
        output_path (Optional[str]): Target filepath. Defaults to 'output/final_output.csv'.

    Returns:
        str: Absolute path of the saved CSV file.
    """
    if output_path is None:
        output_dir = os.path.join(os.getcwd(), "output")
        output_path = os.path.join(output_dir, "final_output.csv")
    else:
        output_dir = os.path.dirname(output_path)

    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Save to CSV using pandas to ensure proper escaping of quotes and commas
    output_df.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
        quoting=csv.QUOTE_MINIMAL
    )
    
    return os.path.abspath(output_path)
