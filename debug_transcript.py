import json

transcript_path = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\brain\0c313aa3-b899-49bf-8e03-a4fa8847d378\.system_generated\logs\transcript_full.jsonl"

with open(transcript_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        data = json.loads(line)
        text = json.dumps(data)
        if "SHP00001" in text:
            print(f"Step {i}: type={data.get('type')}, keys={list(data.keys())}")
            # print part of text containing SHP00001
            idx = text.find("SHP00001")
            print("Snippet around SHP00001:")
            print(text[max(0, idx-100):min(len(text), idx+200)])
            break
