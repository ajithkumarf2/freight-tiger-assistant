import json

transcript_path = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\brain\0c313aa3-b899-49bf-8e03-a4fa8847d378\.system_generated\logs\transcript_full.jsonl"

with open(transcript_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if "SHP00001" in line:
            print(f"Line {i} length: {len(line)}")
            data = json.loads(line)
            print(f"Step {i}: type={data.get('type')}, source={data.get('source')}")
