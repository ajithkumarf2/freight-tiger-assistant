import json

path = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\brain\0c313aa3-b899-49bf-8e03-a4fa8847d378\.system_generated\logs\transcript_full.jsonl"
with open(path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i == 0:
            data = json.loads(line)
            print("Step 0 keys:", list(data.keys()))
            print("Step 0 content:", data.get("content"))
            break
