import json

path = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\brain\0c313aa3-b899-49bf-8e03-a4fa8847d378\.system_generated\logs\transcript_full.jsonl"
with open(path, "r", encoding="utf-8") as f:
    for line_no, line in enumerate(f):
        if "SHP02940" in line:
            print(f"Found SHP02940 at line {line_no}, line length {len(line)}")
            data = json.loads(line)
            print("Keys:", list(data.keys()))
            if "content" in data:
                print("Content length:", len(data["content"]))
