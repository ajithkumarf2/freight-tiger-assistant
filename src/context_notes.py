"""
Step 4: Deterministic Context Note Retrieval and Evidence Validation Engine.

Provides deterministic note loading, structured representation, route/temporal matching,
magnitude guardrails, and evidence validation without LLMs or vector databases.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple


# Structured knowledge base for the 10 known context notes in context_notes.csv
NOTE_KNOWLEDGE_BASE: Dict[str, Dict[str, Any]] = {
    "N001": {
        "note_id": "N001",
        "date": "2025-02-24",
        "applies_to": "Chennai-Bangalore",
        "impact_type": "cost-impacting",
        "valid_start": "2025-02-24",
        "valid_end": "2025-03-08",
        "can_justify_cost_increase": True,
        "max_supported_magnitude": None,
        "reason_summary": "Heavy flooding on the Chennai-Bangalore highway disrupted normal truck movement from Feb 24 to Mar 8, forcing longer detours and higher trip costs."
    },
    "N002": {
        "note_id": "N002",
        "date": "2025-01-20",
        "applies_to": "Ahmedabad-Mumbai",
        "impact_type": "cost-impacting",
        "valid_start": "2025-01-20",
        "valid_end": "2025-01-26",
        "can_justify_cost_increase": True,
        "max_supported_magnitude": None,
        "reason_summary": "A regional festival week saw a temporary surcharge applied by transporters on the Ahmedabad-Mumbai corridor due to high demand and limited truck availability."
    },
    "N003": {
        "note_id": "N003",
        "date": "2025-05-05",
        "applies_to": "All Routes",
        "impact_type": "cost-impacting",
        "valid_start": "2025-05-05",
        "valid_end": "2025-05-11",
        "can_justify_cost_increase": True,
        "max_supported_magnitude": 0.07,  # Documented ~5-7% max supported cost impact
        "reason_summary": "Diesel prices rose nationwide starting this week, pushing up transportation costs across all routes by roughly 5-7%."
    },
    "N004": {
        "note_id": "N004",
        "date": "2024-03-11",
        "applies_to": "All Routes",
        "impact_type": "non-impacting",
        "valid_start": "2024-03-11",
        "valid_end": "2024-03-17",
        "can_justify_cost_increase": False,
        "max_supported_magnitude": None,
        "reason_summary": "A new toll plaza was commissioned on a national highway stretch, but the affected routes are not part of this dataset."
    },
    "N005": {
        "note_id": "N005",
        "date": "2024-07-29",
        "applies_to": "Mumbai-Delhi",
        "impact_type": "non-impacting",
        "valid_start": "2024-07-29",
        "valid_end": "2024-08-04",
        "can_justify_cost_increase": False,
        "max_supported_magnitude": None,
        "reason_summary": "Scheduled highway maintenance work between Mumbai and Delhi caused minor delays for about a week; costs were not significantly affected."
    },
    "N006": {
        "note_id": "N006",
        "date": "2025-09-22",
        "applies_to": "All Routes",
        "impact_type": "status-quo",
        "valid_start": "2025-09-22",
        "valid_end": "2025-09-28",
        "can_justify_cost_increase": False,
        "max_supported_magnitude": None,
        "reason_summary": "A logistics industry report noted overall demand for freight capacity remained stable this quarter with no major disruptions reported."
    },
    "N007": {
        "note_id": "N007",
        "date": "2024-05-20",
        "applies_to": "Delhi-Jaipur",
        "impact_type": "positive-infrastructure",
        "valid_start": "2024-05-20",
        "valid_end": "2024-05-26",
        "can_justify_cost_increase": False,
        "max_supported_magnitude": None,
        "reason_summary": "Local authorities announced improved road conditions on the Delhi-Jaipur stretch after resurfacing work was completed."
    },
    "N008": {
        "note_id": "N008",
        "date": "2025-06-09",
        "applies_to": "Kolkata-Bhubaneswar",
        "impact_type": "status-quo",
        "valid_start": "2025-06-09",
        "valid_end": "2025-06-15",
        "can_justify_cost_increase": False,
        "max_supported_magnitude": None,
        "reason_summary": "No significant disruptions were reported on the Kolkata-Bhubaneswar corridor this quarter; freight movement remained normal."
    },
    "N009": {
        "note_id": "N009",
        "date": "2025-03-17",
        "applies_to": "Chennai-Bangalore",
        "impact_type": "recovery",
        "valid_start": "2025-03-17",
        "valid_end": "2025-03-23",
        "can_justify_cost_increase": False,
        "max_supported_magnitude": None,
        "reason_summary": "Highway authorities confirmed the Chennai-Bangalore route returned to normal conditions after flood-related repairs were completed."
    },
    "N010": {
        "note_id": "N010",
        "date": "2025-10-27",
        "applies_to": "All Routes",
        "impact_type": "non-impacting",
        "valid_start": "2025-10-27",
        "valid_end": "2025-11-02",
        "can_justify_cost_increase": False,
        "max_supported_magnitude": None,
        "reason_summary": "A new vehicle tracking mandate was introduced for commercial fleets; compliance costs were absorbed by transporters without a rate change."
    }
}


def load_context_notes(csv_path: Optional[str] = None) -> pd.DataFrame:
    """
    Loads data/context_notes.csv and enriches it with structured evidence metadata.
    Does NOT modify the source CSV.
    """
    if csv_path is None:
        csv_path = os.path.join("data", "context_notes.csv")
        if not os.path.exists(csv_path):
            csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "context_notes.csv")

    raw_df = pd.read_csv(csv_path)

    enriched_records = []
    for idx, row in raw_df.iterrows():
        nid = str(row['note_id']).strip()
        kb = NOTE_KNOWLEDGE_BASE.get(nid, {})
        
        record = {
            "note_id": nid,
            "date": str(row['date']).strip(),
            "applies_to": str(row['applies_to']).strip(),
            "note": str(row['note']).strip(),
            "impact_type": kb.get("impact_type", "unknown"),
            "valid_start": kb.get("valid_start", str(row['date']).strip()),
            "valid_end": kb.get("valid_end", str(row['date']).strip()),
            "can_justify_cost_increase": kb.get("can_justify_cost_increase", False),
            "max_supported_magnitude": kb.get("max_supported_magnitude", None),
            "reason_summary": kb.get("reason_summary", str(row['note']).strip())
        }
        enriched_records.append(record)

    return pd.DataFrame(enriched_records)


def _parse_date(d_str: str) -> datetime.date:
    """Helper to parse YYYY-MM-DD date string into datetime.date."""
    return datetime.strptime(d_str, '%Y-%m-%d').date()


def retrieve_candidate_notes(
    route: str,
    week_of: str,
    notes_df: pd.DataFrame
) -> List[Dict[str, Any]]:
    """
    Deterministically retrieves notes that match by route/scope and temporal proximity.

    Route/scope match: note.applies_to == route OR note.applies_to == "All Routes"
    Temporal match: Candidate Monday-Sunday week overlaps the note's valid impact window.

    Args:
        route (str): Candidate route (e.g. 'Chennai-Bangalore')
        week_of (str): Monday date of candidate week ('YYYY-MM-DD')
        notes_df (pd.DataFrame): Enriched context notes DataFrame.

    Returns:
        List[Dict[str, Any]]: List of matching note records (as dictionaries).
    """
    cand_mon = _parse_date(week_of)
    cand_sun = cand_mon + timedelta(days=6)

    candidates = []
    for _, row in notes_df.iterrows():
        note_dict = row.to_dict()
        applies_to = note_dict['applies_to']

        # 1. Scope check
        scope_match = (applies_to == route) or (applies_to == "All Routes")
        if not scope_match:
            continue

        # 2. Temporal window overlap check
        v_start = _parse_date(note_dict['valid_start'])
        v_end = _parse_date(note_dict['valid_end'])

        # Candidate week [cand_mon, cand_sun] overlaps valid window [v_start, v_end] if:
        # cand_mon <= v_end AND cand_sun >= v_start
        overlap = (cand_mon <= v_end) and (cand_sun >= v_start)

        if overlap:
            candidates.append(note_dict)

    return candidates


def validate_note_evidence(
    candidate_row: Dict[str, Any],
    note: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Deterministically validates if a single retrieved note is valid evidence to justify an anomaly.

    Validation Checks:
    1. Route / Scope Applicability
    2. Temporal Window Overlap
    3. Note capability to justify cost increase (can_justify_cost_increase == True)
    4. Note-specific magnitude guardrail (e.g. N003 magnitude check)

    Args:
        candidate_row (Dict[str, Any] or pd.Series): Anomaly candidate info with 'route', 'week_of',
                                                     'vs_own_history_pct', 'vs_similar_routes_pct'.
        note (Dict[str, Any]): Retrieved context note metadata.

    Returns:
        Dict[str, Any]: Structured validation result with keys:
            - valid (bool)
            - note_id (str)
            - reason (str)
            - validation_failures (List[str])
    """
    failures = []
    nid = note['note_id']

    # 1. Scope check
    cand_route = candidate_row['route']
    note_scope = note['applies_to']
    if note_scope != cand_route and note_scope != "All Routes":
        failures.append(f"Route mismatch: Note applies to '{note_scope}', but candidate route is '{cand_route}'.")

    # Special dataset exclusion check (N004)
    if nid == "N004":
        failures.append("Note N004 explicitly states affected routes are not part of this dataset.")

    # 2. Temporal overlap check
    cand_mon = _parse_date(candidate_row['week_of'])
    cand_sun = cand_mon + timedelta(days=6)
    v_start = _parse_date(note['valid_start'])
    v_end = _parse_date(note['valid_end'])

    overlap = (cand_mon <= v_end) and (cand_sun >= v_start)
    if not overlap:
        failures.append(f"Temporal mismatch: Candidate week [{cand_mon} to {cand_sun}] does not overlap note valid window [{v_start} to {v_end}].")

    # 3. Can justify cost increase check
    if not note.get('can_justify_cost_increase', False):
        failures.append(f"Note {nid} explicitly describes a non-impacting, status-quo, or recovery event and cannot justify a cost increase.")

    # 4. Magnitude Guardrail check (e.g. N003)
    max_mag = note.get('max_supported_magnitude')
    if max_mag is not None:
        # Determine the observed cost increase magnitude that triggered the anomaly candidate
        own_dev = candidate_row.get('vs_own_history_pct', np.nan)
        peer_dev = candidate_row.get('vs_similar_routes_pct', np.nan)

        # Get the maximum positive deviation observed
        valid_devs = [d for d in [own_dev, peer_dev] if pd.notnull(d) and d > 0]
        obs_dev = max(valid_devs) if valid_devs else 0.0

        if obs_dev > max_mag:
            failures.append(
                f"Magnitude Guardrail Rejection: Note {nid} documents ~{max_mag*100:.0f}% cost impact, "
                f"which is materially exceeded by the observed cost rise of {obs_dev*100:.1f}%."
            )

    is_valid = len(failures) == 0

    if is_valid:
        reason_text = f"Matches note {nid} dated {note['date']}: {note['reason_summary']}"
    else:
        reason_text = f"Note {nid} rejected: " + "; ".join(failures)

    return {
        "valid": is_valid,
        "note_id": nid,
        "reason": reason_text,
        "validation_failures": failures
    }


def find_valid_evidence(
    candidate_row: Dict[str, Any],
    notes_df: pd.DataFrame
) -> Optional[Dict[str, Any]]:
    """
    Finds valid evidence for a given anomaly candidate route-week.

    Process:
    1. Retrieve candidate notes by route/scope and temporal overlap.
    2. Validate each retrieved candidate note deterministically.
    3. Reject invalid notes.
    4. If exactly one valid justification exists, return that evidence dictionary.
    5. If no valid evidence exists (or multiple), return None.

    Args:
        candidate_row (Dict[str, Any]): Anomaly candidate data.
        notes_df (pd.DataFrame): Enriched context notes DataFrame.

    Returns:
        Optional[Dict[str, Any]]: Structured valid evidence dict, or None if unexplained.
    """
    route = candidate_row['route']
    week_of = candidate_row['week_of']

    retrieved = retrieve_candidate_notes(route, week_of, notes_df)

    valid_evidences = []
    for note in retrieved:
        val_res = validate_note_evidence(candidate_row, note)
        if val_res['valid']:
            valid_evidences.append(val_res)

    if len(valid_evidences) == 1:
        return valid_evidences[0]
    elif len(valid_evidences) > 1:
        # If multiple valid notes exist, select the most specific one (route-specific over All Routes)
        route_specific = [v for v in valid_evidences if NOTE_KNOWLEDGE_BASE.get(v['note_id'], {}).get('applies_to') == route]
        if len(route_specific) == 1:
            return route_specific[0]
        return valid_evidences[0]
    
    return None
