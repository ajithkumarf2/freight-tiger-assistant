import csv
from datetime import datetime, timedelta
from collections import defaultdict

shipment_path = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\scratch\freight-tiger-assistant\data\shipment_records.csv"

route_stats = defaultdict(lambda: {'count': 0, 'route_type': None, 'dates': []})

with open(shipment_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        route = f"{r['origin']}-{r['destination']}"
        route_stats[route]['count'] += 1
        route_stats[route]['route_type'] = r['route_type']
        d = datetime.strptime(r['shipment_date'], '%Y-%m-%d').date()
        route_stats[route]['dates'].append(d)

print("Route detailed stats:")
for route, stats in sorted(route_stats.items()):
    min_d = min(stats['dates'])
    max_d = max(stats['dates'])
    print(f"Route: {route:20s} | Type: {stats['route_type']:6s} | Count: {stats['count']:4d} | Date range: {min_d} to {max_d}")
