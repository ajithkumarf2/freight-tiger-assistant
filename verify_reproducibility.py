import os
import pandas as pd
from run_pipeline import run_full_pipeline

print("=== STARTING TWO-RUN REPRODUCIBILITY CHECK ===")

out_path_1 = "output/run1_output.csv"
out_path_2 = "output/run2_output.csv"

res1 = run_full_pipeline(output_csv_path=out_path_1)
res2 = run_full_pipeline(output_csv_path=out_path_2)

# Use keep_default_na=False so empty strings "" are not converted to NaN
df1 = pd.read_csv(out_path_1, dtype=str, keep_default_na=False)
df2 = pd.read_csv(out_path_2, dtype=str, keep_default_na=False)

deterministic_cols = [
    "route",
    "week_of",
    "cost_per_tonne_km",
    "vs_own_history",
    "vs_similar_routes",
    "flagged",
    "matched_note_id"
]

print("\n--- Comparing Deterministic Fields between Run 1 and Run 2 ---")
cols_match = True
for col in deterministic_cols:
    equals = (df1[col] == df2[col]).all()
    print(f"Column '{col:20s}': Identical? {equals}")
    if not equals:
        cols_match = False

print("\n--- Reproducibility Verdict ---")
if cols_match:
    print("REPRODUCIBILITY CHECK PASSED: All 7 deterministic fields are 100% IDENTICAL across runs!")
else:
    print("REPRODUCIBILITY CHECK FAILED: Mismatch detected in deterministic fields.")

# Clean up temp run CSVs
if os.path.exists(out_path_1):
    os.remove(out_path_1)
if os.path.exists(out_path_2):
    os.remove(out_path_2)
