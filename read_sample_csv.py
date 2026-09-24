import csv

sample_out_path = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\scratch\freight-tiger-assistant\data\sample_output_format_v2.csv"

with open(sample_out_path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)
