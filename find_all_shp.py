import os

search_dir = r"C:\Users\Ajithkumar\.gemini"
for root, dirs, files in os.walk(search_dir):
    for f in files:
        filepath = os.path.join(root, f)
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
                if "SHP02940" in content:
                    print("Found SHP02940 in:", filepath)
        except Exception:
            pass
