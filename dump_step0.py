import json

transcript_path = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\brain\0c313aa3-b899-49bf-8e03-a4fa8847d378\.system_generated\logs\transcript_full.jsonl"

with open(transcript_path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        data = json.loads(line)
        if i == 0:
            c = data["content"]
            print("Step 0 content length:", len(c))
            with open("step0_content.txt", "w", encoding="utf-8") as out:
                out.write(c)
            break
