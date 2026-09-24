import shutil

src = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\brain\0c313aa3-b899-49bf-8e03-a4fa8847d378\DATA_ANALYSIS.md"
dst = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\scratch\freight-tiger-assistant\DATA_ANALYSIS.md"

shutil.copy(src, dst)
print(f"Copied {src} -> {dst}")
