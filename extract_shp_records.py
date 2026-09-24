import json

path = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\brain\0c313aa3-b899-49bf-8e03-a4fa8847d378\.system_generated\logs\transcript_full.jsonl"

with open(path, "r", encoding="utf-8") as f:
    for line_no, line in enumerate(f):
        if "SHP00001" in line:
            print(f"SHP00001 at line {line_no}")
            data = json.loads(line)
            print("Type:", data.get("type"))
            # Print keys and structure
            for k, v in data.items():
                if isinstance(v, str) and "SHP00001" in v:
                    print(f"Key '{k}' contains SHP00001. Length: {len(v)}")
                    # extract lines starting with SHP or shipment_id
                    shp_lines = [l.strip() for l in v.split("\n") if l.strip().startswith("SHP") or l.strip().startswith("shipment_id")]
                    print(f"Extracted {len(shp_lines)} lines")
                    if len(shp_lines) > 100:
                        with open(r"C:\Users\Ajithkumar\.gemini\antigravity-ide\scratch\freight-tiger-assistant\data\shipment_records.csv", "w", encoding="utf-8") as out:
                            out.write("\n".join(shp_lines) + "\n")
                        print("Saved to shipment_records.csv successfully!")
                        break
