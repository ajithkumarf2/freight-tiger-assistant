"""
Tests for Step 3: Deterministic Anomaly Candidate Detection Engine.
"""

import pytest
import pandas as pd
import numpy as np
from src.anomaly_detector import detect_anomaly_candidates
from src.config import ANOMALY_THRESHOLD


def make_test_df(history_pct, peer_pct, route="TestRoute", week_of="2024-01-01"):
    return pd.DataFrame([{
        'route': route,
        'week_of': week_of,
        'vs_own_history_pct': history_pct,
        'vs_similar_routes_pct': peer_pct
    }])


# Test 1: history = 25%, peer = 5% -> Expected = True
def test_case_1_history_high_peer_low():
    df = make_test_df(0.25, 0.05)
    res = detect_anomaly_candidates(df)
    assert res.loc[0, 'is_anomaly_candidate'] == True


# Test 2: history = 5%, peer = 25% -> Expected = True
def test_case_2_history_low_peer_high():
    df = make_test_df(0.05, 0.25)
    res = detect_anomaly_candidates(df)
    assert res.loc[0, 'is_anomaly_candidate'] == True


# Test 3: history = 10%, peer = 15% -> Expected = False
def test_case_3_both_below_threshold():
    df = make_test_df(0.10, 0.15)
    res = detect_anomaly_candidates(df)
    assert res.loc[0, 'is_anomaly_candidate'] == False


# Test 4: history = 20%, peer = 5% -> Expected = True
def test_case_4_exact_threshold():
    df = make_test_df(0.20, 0.05)
    res = detect_anomaly_candidates(df)
    assert res.loc[0, 'is_anomaly_candidate'] == True


# Test 5: history = -25%, peer = -30% -> Expected = False
def test_case_5_negative_deviations():
    df = make_test_df(-0.25, -0.30)
    res = detect_anomaly_candidates(df)
    assert res.loc[0, 'is_anomaly_candidate'] == False


# Test 6: history = NaN, peer = 25% -> Expected = True
def test_case_6_nan_history_peer_high():
    df = make_test_df(np.nan, 0.25)
    res = detect_anomaly_candidates(df)
    assert res.loc[0, 'is_anomaly_candidate'] == True


# Test 7: history = 25%, peer = NaN -> Expected = True
def test_case_7_history_high_nan_peer():
    df = make_test_df(0.25, np.nan)
    res = detect_anomaly_candidates(df)
    assert res.loc[0, 'is_anomaly_candidate'] == True


# Test 8: history = NaN, peer = NaN -> Expected = False
def test_case_8_both_nan():
    df = make_test_df(np.nan, np.nan)
    res = detect_anomaly_candidates(df)
    assert res.loc[0, 'is_anomaly_candidate'] == False


# Test 9: history = 19.99%, peer = 19.99% -> Expected = False
def test_case_9_just_below_threshold():
    df = make_test_df(0.1999, 0.1999)
    res = detect_anomaly_candidates(df)
    assert res.loc[0, 'is_anomaly_candidate'] == False


# Known sample case validations
def test_sample_case_delhi_jaipur():
    # Delhi-Jaipur / 2024-11-11: history = +35.5%, peer = +21.0% -> True
    df = make_test_df(0.355, 0.210, route="Delhi-Jaipur", week_of="2024-11-11")
    res = detect_anomaly_candidates(df)
    assert res.loc[0, 'is_anomaly_candidate'] == True


def test_sample_case_ahmedabad_mumbai():
    # Ahmedabad-Mumbai / 2025-01-20: history = +29.5%, peer = +22.5% -> True
    df = make_test_df(0.295, 0.225, route="Ahmedabad-Mumbai", week_of="2025-01-20")
    res = detect_anomaly_candidates(df)
    assert res.loc[0, 'is_anomaly_candidate'] == True


def test_sample_case_mumbai_pune():
    # Mumbai-Pune / 2025-09-15: history = +9.2%, peer = +23.6% -> True
    df = make_test_df(0.092, 0.236, route="Mumbai-Pune", week_of="2025-09-15")
    res = detect_anomaly_candidates(df)
    assert res.loc[0, 'is_anomaly_candidate'] == True
