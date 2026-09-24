"""
Tests for Step 4: Deterministic Context Note Retrieval and Evidence Validation Engine.
"""

import pytest
import pandas as pd
import numpy as np
from src.context_notes import (
    load_context_notes,
    retrieve_candidate_notes,
    validate_note_evidence,
    find_valid_evidence,
    NOTE_KNOWLEDGE_BASE
)


@pytest.fixture
def notes_df():
    return load_context_notes()


def test_load_context_notes(notes_df):
    assert len(notes_df) == 10
    assert "N001" in notes_df['note_id'].values
    assert "N010" in notes_df['note_id'].values


# Test 1: Exact route match
def test_exact_route_match(notes_df):
    candidates = retrieve_candidate_notes("Ahmedabad-Mumbai", "2025-01-20", notes_df)
    note_ids = [c['note_id'] for c in candidates]
    assert "N002" in note_ids


# Test 2: All Routes scope match
def test_all_routes_scope_match(notes_df):
    candidates = retrieve_candidate_notes("Delhi-Jaipur", "2025-05-05", notes_df)
    note_ids = [c['note_id'] for c in candidates]
    assert "N003" in note_ids


# Test 3: Wrong route rejection
def test_wrong_route_rejection(notes_df):
    cand_row = {'route': 'Delhi-Jaipur', 'week_of': '2025-02-24', 'vs_own_history_pct': 0.25, 'vs_similar_routes_pct': 0.10}
    val = validate_note_evidence(cand_row, NOTE_KNOWLEDGE_BASE['N001'])
    assert val['valid'] == False
    assert any("Route mismatch" in f for f in val['validation_failures'])


# Test 4: Exact valid week for N001
def test_n001_exact_valid_week(notes_df):
    cand_row = {'route': 'Chennai-Bangalore', 'week_of': '2025-02-24', 'vs_own_history_pct': 0.30, 'vs_similar_routes_pct': 0.25}
    evidence = find_valid_evidence(cand_row, notes_df)
    assert evidence is not None
    assert evidence['note_id'] == 'N001'
    assert evidence['valid'] == True


# Test 5: N001 second valid week (overlapping window Feb 24 - Mar 8)
def test_n001_second_valid_week(notes_df):
    cand_row = {'route': 'Chennai-Bangalore', 'week_of': '2025-03-03', 'vs_own_history_pct': 0.28, 'vs_similar_routes_pct': 0.22}
    evidence = find_valid_evidence(cand_row, notes_df)
    assert evidence is not None
    assert evidence['note_id'] == 'N001'
    assert evidence['valid'] == True


# Test 6: N001 expired after Mar 8
def test_n001_expired_after_march_8(notes_df):
    cand_row = {'route': 'Chennai-Bangalore', 'week_of': '2025-04-07', 'vs_own_history_pct': 0.25, 'vs_similar_routes_pct': 0.20}
    evidence = find_valid_evidence(cand_row, notes_df)
    assert evidence is None


# Test 7: N002 valid festival week
def test_n002_valid_festival_week(notes_df):
    cand_row = {'route': 'Ahmedabad-Mumbai', 'week_of': '2025-01-20', 'vs_own_history_pct': 0.295, 'vs_similar_routes_pct': 0.225}
    evidence = find_valid_evidence(cand_row, notes_df)
    assert evidence is not None
    assert evidence['note_id'] == 'N002'
    assert evidence['valid'] == True


# Test 8: N002 expired after festival week
def test_n002_expired_after_festival_week(notes_df):
    cand_row = {'route': 'Ahmedabad-Mumbai', 'week_of': '2025-01-27', 'vs_own_history_pct': 0.25, 'vs_similar_routes_pct': 0.20}
    evidence = find_valid_evidence(cand_row, notes_df)
    assert evidence is None


# Test 9: N004 rejection (toll plaza note for non-dataset routes)
def test_n004_rejection(notes_df):
    cand_row = {'route': 'Delhi-Jaipur', 'week_of': '2024-03-11', 'vs_own_history_pct': 0.25, 'vs_similar_routes_pct': 0.20}
    evidence = find_valid_evidence(cand_row, notes_df)
    assert evidence is None


# Test 10: N005 rejection (highway maintenance with no cost impact)
def test_n005_rejection(notes_df):
    cand_row = {'route': 'Mumbai-Delhi', 'week_of': '2024-07-29', 'vs_own_history_pct': 0.25, 'vs_similar_routes_pct': 0.20}
    evidence = find_valid_evidence(cand_row, notes_df)
    assert evidence is None


# Test 11: N006 rejection (stable demand report)
def test_n006_rejection(notes_df):
    cand_row = {'route': 'Mumbai-Pune', 'week_of': '2025-09-15', 'vs_own_history_pct': 0.092, 'vs_similar_routes_pct': 0.236}
    evidence = find_valid_evidence(cand_row, notes_df)
    assert evidence is None


# Test 12: N007 rejection (improved road conditions)
def test_n007_rejection(notes_df):
    cand_row = {'route': 'Delhi-Jaipur', 'week_of': '2024-05-20', 'vs_own_history_pct': 0.25, 'vs_similar_routes_pct': 0.20}
    evidence = find_valid_evidence(cand_row, notes_df)
    assert evidence is None


# Test 13: N008 rejection (normal freight movement)
def test_n008_rejection(notes_df):
    cand_row = {'route': 'Kolkata-Bhubaneswar', 'week_of': '2025-06-09', 'vs_own_history_pct': 0.25, 'vs_similar_routes_pct': 0.20}
    evidence = find_valid_evidence(cand_row, notes_df)
    assert evidence is None


# Test 14: N009 rejection (return to normal / recovery note)
def test_n009_rejection(notes_df):
    cand_row = {'route': 'Chennai-Bangalore', 'week_of': '2025-03-17', 'vs_own_history_pct': 0.25, 'vs_similar_routes_pct': 0.20}
    evidence = find_valid_evidence(cand_row, notes_df)
    assert evidence is None


# Test 15: N010 rejection (fleet tracking cost absorbed without rate change)
def test_n010_rejection(notes_df):
    cand_row = {'route': 'Delhi-Chennai', 'week_of': '2025-10-27', 'vs_own_history_pct': 0.25, 'vs_similar_routes_pct': 0.20}
    evidence = find_valid_evidence(cand_row, notes_df)
    assert evidence is None


# Test 16: N003 magnitude guardrail (20%+ anomaly on 2025-05-05 materially exceeds 5-7% diesel impact)
def test_n003_magnitude_guardrail(notes_df):
    # Case with 25% anomaly cost rise -> N003 documents only ~5-7% impact -> MUST BE REJECTED
    cand_row_high = {'route': 'Delhi-Jaipur', 'week_of': '2025-05-05', 'vs_own_history_pct': 0.25, 'vs_similar_routes_pct': 0.20}
    evidence_high = find_valid_evidence(cand_row_high, notes_df)
    assert evidence_high is None

    # Case with 5% cost rise (below max 7% supported) -> N003 qualifies
    cand_row_modest = {'route': 'Delhi-Jaipur', 'week_of': '2025-05-05', 'vs_own_history_pct': 0.05, 'vs_similar_routes_pct': 0.04}
    val = validate_note_evidence(cand_row_modest, NOTE_KNOWLEDGE_BASE['N003'])
    assert val['valid'] == True


# Test 17: No valid evidence returns None
def test_no_valid_evidence_returns_none(notes_df):
    cand_row = {'route': 'Delhi-Jaipur', 'week_of': '2024-11-11', 'vs_own_history_pct': 0.355, 'vs_similar_routes_pct': 0.210}
    evidence = find_valid_evidence(cand_row, notes_df)
    assert evidence is None


# Test 18: Valid evidence returns correct note_id
def test_valid_evidence_returns_correct_note_id(notes_df):
    cand_row = {'route': 'Ahmedabad-Mumbai', 'week_of': '2025-01-20', 'vs_own_history_pct': 0.295, 'vs_similar_routes_pct': 0.225}
    evidence = find_valid_evidence(cand_row, notes_df)
    assert evidence is not None
    assert evidence['note_id'] == 'N002'
    assert evidence['valid'] == True
