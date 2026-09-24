import os

search_dirs = [
    r"C:\Users\Ajithkumar\.gemini",
    r"C:\Users\Ajithkumar\Downloads",
    r"C:\Users\Ajithkumar\Desktop",
]

for sdir in search_dirs:
    if os.path.exists(sdir):
        for root, dirs, files in os.walk(sdir):
            for f in files:
                if "shipment" in f.lower() or "context_notes" in f.lower():
                    print("Found file:", os.path.join(root, f))
