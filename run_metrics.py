"""
Execution script for Step 2 (Metrics), Step 3 (Anomaly Candidate Detection),
Step 4 (Deterministic Note Retrieval & Validation), and Step 5 (Grounded LLM Explanation & Token/Cost Logging).
"""

import os
import pandas as pd
from src.metrics_engine import compute_weekly_route_metrics
from src.anomaly_detector import detect_anomaly_candidates
from src.context_notes import load_context_notes, find_valid_evidence, retrieve_candidate_notes
from src.llm_explainer import build_llm_input, generate_explanation
from src.llm_usage import usage_tracker


def main():
    usage_tracker.reset()

    csv_path = os.path.join("data", "shipment_records.csv")
    if not os.path.exists(csv_path):
        csv_path = os.path.join(os.path.dirname(__file__), "data", "shipment_records.csv")

    print(f"Loading shipment records from: {csv_path}")
    shipment_df = pd.read_csv(csv_path)
    print(f"Loaded {len(shipment_df)} shipment records.")

    # Step 2: Compute weekly metrics and baselines
    print("\n--- Running Step 2: Deterministic Metrics Calculation ---")
    metrics_df = compute_weekly_route_metrics(shipment_df)
    print(f"Computed metrics for {len(metrics_df)} weekly route records.")

    # Step 3: Detect anomaly candidates
    print("\n--- Running Step 3: Deterministic Anomaly Candidate Detection ---")
    candidate_df = detect_anomaly_candidates(metrics_df)
    
    total_candidates = candidate_df['is_anomaly_candidate'].sum()
    total_records = len(candidate_df)
    print(f"Total Weekly Route Records Evaluated: {total_records}")
    print(f"Total Anomaly Candidates Detected: {total_candidates} ({(total_candidates / total_records) * 100:.1f}%)")

    # Step 4: Deterministic Context Note Retrieval and Evidence Validation
    print("\n--- Running Step 4: Context Note Retrieval & Evidence Validation ---")
    notes_df = load_context_notes()
    print(f"Loaded {len(notes_df)} enriched context notes.")

    candidate_rows = candidate_df[candidate_df['is_anomaly_candidate']].to_dict('records')
    
    # Step 5: LLM Grounded Explanation Generation for Anomaly Candidates
    print("\n--- Running Step 5: LLM Explanation Generation & Token Logging ---")
    
    explanation_results = []
    for cand in candidate_rows:
        evidence = find_valid_evidence(cand, notes_df)
        llm_in = build_llm_input(cand, evidence)
        
        # Generate grounded explanation (uses API key if available, else deterministic fallback)
        llm_out = generate_explanation(llm_in)

        record = {
            "route": cand['route'],
            "week_of": cand['week_of'],
            "cost_per_tonne_km": round(cand['cost_per_tonne_km'], 2),
            "is_candidate": cand['is_anomaly_candidate'],
            "validated_note_id": llm_in['validated_note_id'],
            "llm_input": llm_in,
            "llm_output": llm_out,
            "reason": llm_out.get('reason', '')
        }
        explanation_results.append(record)

    print(f"Generated Grounded Explanations for {len(explanation_results)} Anomaly Candidates.")

    # Print Sample Case Results
    print("\n--- Step 5 Sample Anomaly Candidates Explanation Report ---")
    sample_cases = [
        ("Ahmedabad-Mumbai", "2025-01-20", "Case A: Festival week surcharge (N002)"),
        ("Chennai-Bangalore", "2025-02-24", "Case B: Flood disruption start week (N001)"),
        ("Chennai-Bangalore", "2025-03-03", "Case C: Flood disruption second week (N001)"),
        ("Mumbai-Pune", "2025-09-15", "Case E: Stable demand note distractor (N006 rejected)"),
        ("Mumbai-Delhi", "2024-07-29", "Case F: Maintenance note distractor (N005 rejected)"),
        ("Delhi-Jaipur", "2024-11-11", "Unexplained anomaly spike (No valid note)"),
    ]

    for route, week_of, label in sample_cases:
        item = next((res for res in explanation_results if res['route'] == route and res['week_of'] == week_of), None)
        if item:
            print(f"[{label}]")
            print(f"  Route: {item['route']} | Week: {item['week_of']} | CPTK: {item['cost_per_tonne_km']}")
            print(f"  Validated Note ID: '{item['validated_note_id']}'")
            print(f"  LLM Output JSON: {item['llm_output']}")
            print("-" * 75)

    # Usage and Token Cost Summary
    summary = usage_tracker.get_summary()
    print("\n=== STEP 5 LLM TOKEN & COST LOGGING SUMMARY ===")
    print(f"  Total LLM Calls: {summary['total_llm_calls']}")
    print(f"  Total Input Tokens: {summary['total_input_tokens']}")
    print(f"  Total Output Tokens: {summary['total_output_tokens']}")
    print(f"  Total Tokens: {summary['total_tokens']}")
    print(f"  Total Estimated Cost: ${summary['total_estimated_cost_usd']:.6f} USD")
    print("=================================================")

    return explanation_results


if __name__ == "__main__":
    main()
