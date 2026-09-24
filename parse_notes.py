import csv

notes_path = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\scratch\freight-tiger-assistant\data\context_notes.csv"

with open(notes_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        print(f"ID: {r['note_id']} | Date: {r['date']} | Applies To: {r['applies_to']}")
        print(f"  Note: {r['note']}")
        print("-" * 80)
