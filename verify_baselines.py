import csv
from datetime import datetime, timedelta
from collections import defaultdict

shipment_path = r"C:\Users\Ajithkumar\.gemini\antigravity-ide\scratch\freight-tiger-assistant\data\shipment_records.csv"

# 1. Weekly cost_per_tonne_km per route
weekly_cptk = defaultdict(dict)
route_types = {}

weekly_data = defaultdict(lambda: defaultdict(lambda: {'cost': 0.0, 'tkm': 0.0}))

with open(shipment_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        route = f"{r['origin']}-{r['destination']}"
        rtype = r['route_type']
        route_types[route] = rtype
        
        d = datetime.strptime(r['shipment_date'], '%Y-%m-%d').date()
        mon = d - timedelta(days=d.weekday())
        
        cost = float(r['freight_cost_inr'])
        tkm = float(r['quantity_tonnes']) * float(r['distance_km'])
        
        weekly_data[route][mon]['cost'] += cost
        weekly_data[route][mon]['tkm'] += tkm

for route in weekly_data:
    for mon in weekly_data[route]:
        t_cost = weekly_data[route][mon]['cost']
        t_tkm = weekly_data[route][mon]['tkm']
        weekly_cptk[route][mon] = t_cost / t_tkm if t_tkm > 0 else 0.0

# Verify baseline calculations for the 3 sample output rows
# Row 1: Delhi-Jaipur, 2024-11-11
# Row 2: Ahmedabad-Mumbai, 2025-01-20
# Row 3: Mumbai-Pune, 2025-09-15

samples = [
    ('Delhi-Jaipur', datetime.strptime('2024-11-11', '%Y-%m-%d').date()),
    ('Ahmedabad-Mumbai', datetime.strptime('2025-01-20', '%Y-%m-%d').date()),
    ('Mumbai-Pune', datetime.strptime('2025-09-15', '%Y-%m-%d').date()),
]

print("=== VERIFYING SAMPLE BASELINES ===")
for route, cur_mon in samples:
    cur_cptk = weekly_cptk[route][cur_mon]
    rtype = route_types[route]
    
    # 1. Trailing 8 weeks
    all_mons = sorted(weekly_cptk[route].keys())
    prior_mons = [m for m in all_mons if m < cur_mon]
    trailing_8 = prior_mons[-8:]
    trailing_cptks = [weekly_cptk[route][m] for m in trailing_8]
    own_baseline = sum(trailing_cptks) / len(trailing_cptks) if trailing_cptks else 0
    pct_own = ((cur_cptk - own_baseline) / own_baseline) * 100 if own_baseline else 0
    
    # 2. Peer baseline
    peer_routes = [r for r, t in route_types.items() if t == rtype and r != route]
    peer_cptks = [weekly_cptk[pr][cur_mon] for pr in peer_routes if cur_mon in weekly_cptk[pr]]
    peer_baseline = sum(peer_cptks) / len(peer_cptks) if peer_cptks else 0
    pct_peer = ((cur_cptk - peer_baseline) / peer_baseline) * 100 if peer_baseline else 0
    
    print(f"\nRoute: {route} | Week: {cur_mon} | Route Type: {rtype}")
    print(f"  Current CPTK: {cur_cptk:.4f} (Sample output format shows {cur_cptk:.2f})")
    print(f"  Prior weeks count: {len(trailing_8)} | Trailing values: {[round(v, 4) for v in trailing_cptks]}")
    print(f"  Own Baseline: {own_baseline:.4f} | Diff: {pct_own:+.1f}% vs this route's past average")
    print(f"  Peer Routes: {peer_routes} | Peer CPTKs: {[round(v, 4) for v in peer_cptks]}")
    print(f"  Peer Baseline: {peer_baseline:.4f} | Diff: {pct_peer:+.1f}% vs similar-length routes this week")
