import shutil
import os

user_uploaded_dir = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\brain\0c313aa3-b899-49bf-8e03-a4fa8847d378\.user_uploaded"
data_dir = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\scratch\freight-tiger-assistant\data"

for f in os.listdir(user_uploaded_dir):
    fpath = os.path.join(user_uploaded_dir, f)
    if f.endswith(".csv"):
        with open(fpath, "r", encoding="utf-8") as handle:
            header = handle.readline().strip()
            print(f"File {f} header: {header}")
            if "shipment_id" in header:
                shutil.copy(fpath, os.path.join(data_dir, "shipment_records.csv"))
            elif "note_id" in header and "matched_note_id" not in header:
                shutil.copy(fpath, os.path.join(data_dir, "context_notes.csv"))
            elif "matched_note_id" in header or "vs_own_history" in header:
                shutil.copy(fpath, os.path.join(data_dir, "sample_output_format_v2.csv"))

print("Files in data_dir:")
for d in os.listdir(data_dir):
    print(" -", d, os.path.getsize(os.path.join(data_dir, d)), "bytes")
