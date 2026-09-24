import csv
from datetime import datetime, timedelta
from collections import defaultdict

shipment_path = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\scratch\freight-tiger-assistant\data\shipment_records.csv"

# Group shipments by route and week_of
weekly_data = defaultdict(lambda: defaultdict(list))

with open(shipment_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        route = f"{r['origin']}-{r['destination']}"
        d = datetime.strptime(r['shipment_date'], '%Y-%m-%d').date()
        mon = d - timedelta(days=d.weekday())
        
        cost = float(r['freight_cost_inr'])
        qty = float(r['quantity_tonnes'])
        dist = float(r['distance_km'])
        
        weekly_data[route][mon].append((cost, qty, dist))

# Compute weekly cost_per_tonne_km for a few sample route-weeks
print("Sample Weekly Aggregations:")
for route in sorted(weekly_data.keys()):
    sample_mon = sorted(weekly_data[route].keys())[0]
    ship_list = weekly_data[route][sample_mon]
    
    tot_cost = sum(c for c, q, d in ship_list)
    tot_tonne_km = sum(q * d for c, q, d in ship_list)
    cptk_weighted = tot_cost / tot_tonne_km if tot_tonne_km > 0 else 0
    
    # Compare with mean of individual ratios
    ind_ratios = [c / (q * d) for c, q, d in ship_list]
    cptk_unweighted = sum(ind_ratios) / len(ind_ratios)
    
    print(f"Route: {route:20s} | Week: {sample_mon} | Shipments: {len(ship_list)}")
    print(f"   Weighted (Correct): {cptk_weighted:.4f} | Unweighted mean: {cptk_unweighted:.4f}")
