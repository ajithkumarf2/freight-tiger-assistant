import os

brain_dir = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\brain\0c313aa3-b899-49bf-8e03-a4fa8847d378"

for root, dirs, files in os.walk(brain_dir):
    for f in files:
        path = os.path.join(root, f)
        size = os.path.getsize(path)
        print(f"{f}: {size} bytes ({path})")
