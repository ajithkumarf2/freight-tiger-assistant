import os

search_dirs = [
    r"C:\Users\Ajithkumar\.gemini",
]

for sdir in search_dirs:
    if os.path.exists(sdir):
        for root, dirs, files in os.walk(sdir):
            for f in files:
                if f in ["config.py", "metrics_engine.py", "run_metrics.py", "anomaly_detector.py"]:
                    print("Found file:", os.path.join(root, f))
