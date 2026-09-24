"""
Unit tests for Step 6: Output Generator Engine.
"""

import os
import csv
import tempfile
import pytest
import pandas as pd
from src.output_generator import (
    format_final_output,
    save_final_csv,
    EXPECTED_COLUMNS,
    format_percentage_own_history,
    format_percentage_similar_routes,
    format_cost_per_tonne_km
)


@pytest.fixture
def sample_candidate_df():
    return pd.DataFrame([
        {
            "route": "Delhi-Jaipur",
            "route_type": "Short",
            "week_of": "2024-11-11",
            "cost_per_tonne_km": 4.173,
            "vs_own_history_pct": 0.355,
            "vs_similar_routes_pct": 0.210,
            "is_anomaly_candidate": True
        },
        {
            "route": "Ahmedabad-Mumbai",
            "route_type": "Medium",
            "week_of": "2025-01-20",
            "cost_per_tonne_km": 3.2904,
            "vs_own_history_pct": 0.295,
            "vs_similar_routes_pct": 0.225,
            "is_anomaly_candidate": True
        },
        {
            "route": "Mumbai-Pune",
            "route_type": "Short",
            "week_of": "2025-09-15",
            "cost_per_tonne_km": 3.9808,
            "vs_own_history_pct": 0.092,
            "vs_similar_routes_pct": 0.236,
            "is_anomaly_candidate": True
        },
        {
            "route": "Mumbai-Pune",
            "route_type": "Short",
            "week_of": "2024-01-01",
            "cost_per_tonne_km": 3.3013,
            "vs_own_history_pct": None,
            "vs_similar_routes_pct": -0.05,
            "is_anomaly_candidate": False  # Normal week, should be excluded
        }
    ])


@pytest.fixture
def sample_explanations():
    return [
        {
            "route": "Delhi-Jaipur",
            "week_of": "2024-11-11",
            "validated_note_id": "",
            "reason": "No matching note found for this route or date range. Cost rise looks unexplained and worth a human review."
        },
        {
            "route": "Ahmedabad-Mumbai",
            "week_of": "2025-01-20",
            "validated_note_id": "N002",
            "reason": "Matches note N002 dated 2025-01-20: a regional festival week drove a temporary surcharge on this corridor. The cost rise has a clear explanation."
        },
        {
            "route": "Mumbai-Pune",
            "week_of": "2025-09-15",
            "validated_note_id": "",
            "reason": "The closest note (N006, 2025-09-22) mentions stable demand with no major disruptions -- it does not describe a reason for a cost rise on this route. No genuine justification found; flagged for review."
        }
    ]


# Test 1: Exact column order and no extra columns
def test_exact_column_order(sample_candidate_df, sample_explanations):
    out_df = format_final_output(sample_candidate_df, sample_explanations)
    assert list(out_df.columns) == EXPECTED_COLUMNS


# Test 2: Only anomaly candidates included
def test_only_anomaly_candidates_included(sample_candidate_df, sample_explanations):
    out_df = format_final_output(sample_candidate_df, sample_explanations)
    assert len(out_df) == 3  # 4 rows in input, but 1 is False -> 3 rows output
    assert "2024-01-01" not in out_df["week_of"].values


# Test 3: Cost rounding to 2 decimal places
def test_cost_rounding(sample_candidate_df, sample_explanations):
    out_df = format_final_output(sample_candidate_df, sample_explanations)
    delhi_row = out_df[out_df["route"] == "Delhi-Jaipur"].iloc[0]
    assert delhi_row["cost_per_tonne_km"] == "4.17"
    ahmedabad_row = out_df[out_df["route"] == "Ahmedabad-Mumbai"].iloc[0]
    assert ahmedabad_row["cost_per_tonne_km"] == "3.29"


# Test 4 & 5: Percentage formatting to 1 decimal place
def test_percentage_formatting(sample_candidate_df, sample_explanations):
    out_df = format_final_output(sample_candidate_df, sample_explanations)
    delhi_row = out_df[out_df["route"] == "Delhi-Jaipur"].iloc[0]
    assert delhi_row["vs_own_history"] == "+35.5% vs this route's past average"
    assert delhi_row["vs_similar_routes"] == "+21.0% vs similar-length routes this week"

    pune_row = out_df[out_df["route"] == "Mumbai-Pune"].iloc[0]
    assert pune_row["vs_own_history"] == "+9.2% vs this route's past average"
    assert pune_row["vs_similar_routes"] == "+23.6% vs similar-length routes this week"


# Test 6 & 7 & 8: Correct flagged value and matched_note_id
def test_flagged_and_matched_note_id(sample_candidate_df, sample_explanations):
    out_df = format_final_output(sample_candidate_df, sample_explanations)
    
    # Justified anomaly (N002)
    ahm_row = out_df[out_df["route"] == "Ahmedabad-Mumbai"].iloc[0]
    assert ahm_row["flagged"] == "No (justified)"
    assert ahm_row["matched_note_id"] == "N002"

    # Unexplained anomaly (Delhi-Jaipur)
    delhi_row = out_df[out_df["route"] == "Delhi-Jaipur"].iloc[0]
    assert delhi_row["flagged"] == "Yes"
    assert delhi_row["matched_note_id"] == ""


# Test 9: Reason field CSV safety with commas
def test_reason_csv_safety(sample_candidate_df, sample_explanations):
    out_df = format_final_output(sample_candidate_df, sample_explanations)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_csv = os.path.join(tmpdir, "test_out.csv")
        save_final_csv(out_df, tmp_csv)
        
        # Read back using csv.reader
        with open(tmp_csv, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))
            header = reader[0]
            assert header == EXPECTED_COLUMNS
            
            # Row 4 is Mumbai-Pune containing commas in reason
            pune_line = next(r for r in reader if r[0] == "Mumbai-Pune")
            assert len(pune_line) == 8
            assert "(N006, 2025-09-22)" in pune_line[7]


# Test 10: LLM Failure Fallback Handling
def test_llm_failure_fallback(sample_candidate_df):
    # Empty explanations list (simulating missing LLM output)
    empty_explanations = []
    out_df = format_final_output(sample_candidate_df, empty_explanations)

    assert len(out_df) == 3
    for idx, row in out_df.iterrows():
        assert row["flagged"] == "Yes"
        assert row["matched_note_id"] == ""
        assert "unexplained" in row["reason"].lower()


# Test 11, 12, 13: Sample cases validation
def test_sample_output_validation(sample_candidate_df, sample_explanations):
    out_df = format_final_output(sample_candidate_df, sample_explanations)

    # Delhi-Jaipur 2024-11-11
    dj = out_df[(out_df["route"] == "Delhi-Jaipur") & (out_df["week_of"] == "2024-11-11")].iloc[0]
    assert dj["cost_per_tonne_km"] == "4.17"
    assert dj["vs_own_history"] == "+35.5% vs this route's past average"
    assert dj["vs_similar_routes"] == "+21.0% vs similar-length routes this week"
    assert dj["flagged"] == "Yes"
    assert dj["matched_note_id"] == ""

    # Ahmedabad-Mumbai 2025-01-20
    am = out_df[(out_df["route"] == "Ahmedabad-Mumbai") & (out_df["week_of"] == "2025-01-20")].iloc[0]
    assert am["cost_per_tonne_km"] == "3.29"
    assert am["vs_own_history"] == "+29.5% vs this route's past average"
    assert am["vs_similar_routes"] == "+22.5% vs similar-length routes this week"
    assert am["flagged"] == "No (justified)"
    assert am["matched_note_id"] == "N002"

    # Mumbai-Pune 2025-09-15
    mp = out_df[(out_df["route"] == "Mumbai-Pune") & (out_df["week_of"] == "2025-09-15")].iloc[0]
    assert mp["cost_per_tonne_km"] == "3.98"
    assert mp["vs_own_history"] == "+9.2% vs this route's past average"
    assert mp["vs_similar_routes"] == "+23.6% vs similar-length routes this week"
    assert mp["flagged"] == "Yes"
    assert mp["matched_note_id"] == ""
