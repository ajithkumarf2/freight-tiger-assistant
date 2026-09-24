"""
Step 2: Deterministic Metrics Calculation Engine.

Calculates weekly cost per tonne-km per route, trailing own-history baseline (up to 8 prior weeks),
and same-week peer baseline across similar route types.
"""

import pandas as pd
import numpy as np


def compute_weekly_route_metrics(shipment_df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes weekly metrics and baselines from raw shipment records.

    Args:
        shipment_df (pd.DataFrame): Input dataframe containing:
            - origin, destination, route_type, quantity_tonnes, distance_km,
              freight_cost_inr, shipment_date

    Returns:
        pd.DataFrame: Aggregated weekly route metrics with columns:
            - route, route_type, week_of, total_freight_cost_inr, total_tonne_km,
              cost_per_tonne_km, own_history_baseline, vs_own_history_pct,
              peer_baseline, vs_similar_routes_pct
    """
    df = shipment_df.copy()

    # Ensure date parsing and Monday week_of computation
    df['shipment_date'] = pd.to_datetime(df['shipment_date'])
    # Monday of the week
    df['week_of'] = df['shipment_date'].dt.to_period('W-SUN').dt.start_time.dt.strftime('%Y-%m-%d')
    
    # Construct route identifier
    if 'route' not in df.columns:
        df['route'] = df['origin'].astype(str) + '-' + df['destination'].astype(str)

    # Compute tonne-km per shipment
    df['tonne_km'] = df['quantity_tonnes'].astype(float) * df['distance_km'].astype(float)
    df['freight_cost_inr'] = df['freight_cost_inr'].astype(float)

    # Aggregate weekly metrics per route
    weekly_agg = df.groupby(['route', 'route_type', 'week_of'], as_index=False).agg(
        total_freight_cost_inr=('freight_cost_inr', 'sum'),
        total_tonne_km=('tonne_km', 'sum')
    )

    # Weekly cost_per_tonne_km = SUM(freight_cost_inr) / SUM(quantity_tonnes * distance_km)
    weekly_agg['cost_per_tonne_km'] = (
        weekly_agg['total_freight_cost_inr'] / weekly_agg['total_tonne_km']
    )

    # Sort deterministically by route and week_of
    weekly_agg = weekly_agg.sort_values(['route', 'week_of']).reset_index(drop=True)

    # 1. Own-history baseline: trailing average of up to 8 prior weeks (strictly excluding current week)
    own_baselines = []
    vs_own_pcts = []

    for route, group in weekly_agg.groupby('route', sort=False):
        cptk_series = group['cost_per_tonne_km'].values
        n = len(cptk_series)
        route_own_b = []
        route_vs_own = []

        for i in range(n):
            if i == 0:
                # No prior history available
                route_own_b.append(np.nan)
                route_vs_own.append(np.nan)
            else:
                # Trailing up to 8 prior weeks
                start_idx = max(0, i - 8)
                prior_vals = cptk_series[start_idx:i]
                b_val = np.mean(prior_vals)
                cur_val = cptk_series[i]
                diff_pct = (cur_val - b_val) / b_val if b_val > 0 else np.nan
                route_own_b.append(b_val)
                route_vs_own.append(diff_pct)

        own_baselines.extend(route_own_b)
        vs_own_pcts.extend(route_vs_own)

    weekly_agg['own_history_baseline'] = own_baselines
    weekly_agg['vs_own_history_pct'] = vs_own_pcts

    # 2. Peer baseline: same-week average cost_per_tonne_km of all OTHER routes sharing the same route_type
    peer_baselines = []
    vs_peer_pcts = []

    # Map week_of + route_type to CPTK per route
    # Create lookup map: (week_of, route_type) -> list of (route, cptk)
    week_type_map = {}
    for idx, row in weekly_agg.iterrows():
        key = (row['week_of'], row['route_type'])
        if key not in week_type_map:
            week_type_map[key] = []
        week_type_map[key].append((row['route'], row['cost_per_tonne_km']))

    for idx, row in weekly_agg.iterrows():
        key = (row['week_of'], row['route_type'])
        cur_route = row['route']
        cur_cptk = row['cost_per_tonne_km']

        peer_vals = [cptk for r, cptk in week_type_map[key] if r != cur_route]
        if peer_vals:
            p_b = np.mean(peer_vals)
            p_diff = (cur_cptk - p_b) / p_b if p_b > 0 else np.nan
        else:
            p_b = np.nan
            p_diff = np.nan

        peer_baselines.append(p_b)
        vs_peer_pcts.append(p_diff)

    weekly_agg['peer_baseline'] = peer_baselines
    weekly_agg['vs_similar_routes_pct'] = vs_peer_pcts

    return weekly_agg
