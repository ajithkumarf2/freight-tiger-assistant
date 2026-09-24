import json

transcript_path = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\brain\0c313aa3-b899-49bf-8e03-a4fa8847d378\.system_generated\logs\transcript_full.jsonl"
output_path = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\scratch\freight-tiger-assistant\data\shipment_records.csv"

with open(transcript_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "shipment_id,origin,destination" in line:
            data = json.loads(line)
            print(f"Match on step {i}, type={data.get('type')}")
            # let's find the content string anywhere in data
            s = json.dumps(data)
            idx = s.find("shipment_id,origin,destination")
            pdf_idx = s.find("==Start of PDF==")
            sub = s[idx:pdf_idx] if pdf_idx != -1 else s[idx:]
            # replace escaped newlines
            sub = sub.replace("\\n", "\n").replace("\\r", "").replace('\\"', '"')
            lines = [l.strip() for l in sub.splitlines() if l.strip().startswith("SHP") or l.strip().startswith("shipment_id")]
            print(f"Extracted {len(lines)} lines")
            if len(lines) > 10:
                with open(output_path, "w", encoding="utf-8") as out:
                    out.write("\n".join(lines) + "\n")
                break
