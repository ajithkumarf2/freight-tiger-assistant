import csv
from datetime import datetime, timedelta
from collections import defaultdict

shipment_path = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\scratch\freight-tiger-assistant\data\shipment_records.csv"
notes_path = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\scratch\freight-tiger-assistant\data\context_notes.csv"
sample_out_path = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\scratch\freight-tiger-assistant\data\sample_output_format_v2.csv"

# 1. Shipment Records
shipments = []
with open(shipment_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        shipments.append(row)

print("=== 1. SHIPMENT DATASET ANALYSIS ===")
print("Columns:", list(shipments[0].keys()))
print("Row Count:", len(shipments))

# Check data types and missing values
missing = defaultdict(int)
dates = []
routes = set()
route_types = set()
route_to_type = {}
route_type_routes = defaultdict(set)
materials = set()
transporters = set()

for s in shipments:
    for k, v in s.items():
        if v is None or v.strip() == "":
            missing[k] += 1
    d = datetime.strptime(s['shipment_date'], '%Y-%m-%d').date()
    dates.append(d)
    r = f"{s['origin']}-{s['destination']}"
    routes.add(r)
    rt = s['route_type']
    route_types.add(rt)
    route_to_type[r] = rt
    route_type_routes[rt].add(r)
    materials.add(s['material'])
    transporters.add(s['transporter'])

print("Missing values per column:", dict(missing))
min_date = min(dates)
max_date = max(dates)
print(f"Date Range: {min_date} to {max_date}")
print(f"Unique Routes ({len(routes)}):", sorted(list(routes)))
print("Route Types and Routes:")
for rt, rset in route_type_routes.items():
    print(f"  {rt}: {sorted(list(rset))}")
print("Materials:", sorted(list(materials)))
print("Transporters:", sorted(list(transporters)))

# Calculate week range
weeks = set()
for d in dates:
    # Monday of the week
    mon = d - timedelta(days=d.weekday())
    weeks.add(mon)

sorted_weeks = sorted(list(weeks))
print(f"Total Weeks: {len(sorted_weeks)}")
print(f"Min Week Monday: {sorted_weeks[0]}")
print(f"Max Week Monday: {sorted_weeks[-1]}")

print("\n=== 2. CONTEXT NOTES ANALYSIS ===")
notes = []
with open(notes_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        notes.append(row)

print("Note Columns:", list(notes[0].keys()))
print("Note Count:", len(notes))
for n in notes:
    print(f"Note ID: {n['note_id']} | Date: {n['date']} | Applies To: {n['applies_to']}")
    print(f"   Text: {n['note']}")

print("\n=== 3. SAMPLE OUTPUT FORMAT V2 ANALYSIS ===")
sample_rows = []
with open(sample_out_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        sample_rows.append(row)

print("Sample Columns:", list(sample_rows[0].keys()))
print("Sample Rows Count:", len(sample_rows))
for r in sample_rows:
    print(r)
