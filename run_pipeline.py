"""
Complete 6-Step Pipeline Execution Script for FreightTiger Shipping Cost Assistant.

Executes:
1. Load shipment records (data/shipment_records.csv)
2. Step 2: Deterministic weekly metrics calculation
3. Step 3: Deterministic anomaly candidate detection
4. Step 4: Deterministic context note retrieval and evidence validation
5. Step 5: Grounded LLM explanation generation and token/cost logging
6. Step 6: Final CSV output generation (output/final_output.csv) and usage log export
"""

import os
import json
import pandas as pd
from src.metrics_engine import compute_weekly_route_metrics
from src.anomaly_detector import detect_anomaly_candidates
from src.context_notes import load_context_notes, find_valid_evidence
from src.llm_explainer import build_llm_input, generate_explanation
from src.llm_usage import usage_tracker
from src.output_generator import format_final_output, save_final_csv


def run_full_pipeline(
    csv_path: str = "data/shipment_records.csv",
    output_csv_path: str = "output/final_output.csv"
):
    usage_tracker.reset()

    if not os.path.exists(csv_path):
        csv_path = os.path.join(os.path.dirname(__file__), "data", "shipment_records.csv")

    print(f"Loading shipment records from: {csv_path}")
    shipment_df = pd.read_csv(csv_path)
    total_shipment_records = len(shipment_df)

    # Step 2: Calculate weekly metrics and baselines
    print("\n--- Running Step 2: Deterministic Metrics Calculation ---")
    metrics_df = compute_weekly_route_metrics(shipment_df)
    total_route_week_obs = len(metrics_df)

    # Step 3: Detect anomaly candidates
    print("\n--- Running Step 3: Deterministic Anomaly Candidate Detection ---")
    candidate_df = detect_anomaly_candidates(metrics_df)
    total_anomaly_candidates = candidate_df['is_anomaly_candidate'].sum()

    # Step 4 & Step 5: Evidence Validation and LLM Explanation Generation
    print("\n--- Running Step 4 & 5: Evidence Validation & LLM Explanations ---")
    notes_df = load_context_notes()
    
    candidate_rows = candidate_df[candidate_df['is_anomaly_candidate']].to_dict('records')
    
    justified_count = 0
    unexplained_count = 0
    explanation_results = []

    for cand in candidate_rows:
        evidence = find_valid_evidence(cand, notes_df)
        llm_in = build_llm_input(cand, evidence)
        llm_out = generate_explanation(llm_in)

        v_note_id = llm_in['validated_note_id']
        if v_note_id != "":
            justified_count += 1
        else:
            unexplained_count += 1

        record = {
            "route": cand['route'],
            "week_of": cand['week_of'],
            "cost_per_tonne_km": cand['cost_per_tonne_km'],
            "validated_note_id": v_note_id,
            "reason": llm_out.get("reason", "")
        }
        explanation_results.append(record)

    # Step 6: Format Final CSV Output
    print("\n--- Running Step 6: Final CSV Formatting & Output Export ---")
    final_output_df = format_final_output(candidate_df, explanation_results)
    final_csv_abs_path = save_final_csv(final_output_df, output_csv_path)

    # Export LLM Token and Cost Usage Log
    usage_summary = usage_tracker.get_summary()
    output_dir = os.path.dirname(final_csv_abs_path)
    usage_log_path = os.path.join(output_dir, "llm_token_cost_log.json")
    with open(usage_log_path, "w", encoding="utf-8") as f:
        json.dump(usage_summary, f, indent=2)

    # Final Pipeline Summary Report
    print("\n=================================================")
    print("      FREIGHTTIGER PIPELINE SUMMARY REPORT       ")
    print("=================================================")
    print(f"Total shipment records:         {total_shipment_records}")
    print(f"Total route-week observations:  {total_route_week_obs}")
    print(f"Total anomaly candidates:       {total_anomaly_candidates}")
    print(f"Total justified anomalies:      {justified_count}")
    print(f"Total unexplained anomalies:    {unexplained_count}")
    print(f"Total LLM calls:                {usage_summary['total_llm_calls']}")
    print(f"Total input tokens:             {usage_summary['total_input_tokens']}")
    print(f"Total output tokens:            {usage_summary['total_output_tokens']}")
    print(f"Total tokens:                   {usage_summary['total_tokens']}")
    print(f"Estimated cost:                 ${usage_summary['total_estimated_cost_usd']:.6f} USD")
    print(f"Final CSV Output File:          {final_csv_abs_path}")
    print(f"Token/Cost Log File:            {usage_log_path}")
    print("=================================================\n")

    return {
        "final_output_df": final_output_df,
        "final_csv_path": final_csv_abs_path,
        "usage_summary": usage_summary,
        "total_shipment_records": total_shipment_records,
        "total_route_week_obs": total_route_week_obs,
        "total_anomaly_candidates": total_anomaly_candidates,
        "justified_count": justified_count,
        "unexplained_count": unexplained_count
    }


if __name__ == "__main__":
    run_full_pipeline()
