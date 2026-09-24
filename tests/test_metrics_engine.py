"""
Tests for Step 2: Deterministic Metrics Calculation Engine.
"""

import pytest
import pandas as pd
import numpy as np
from src.metrics_engine import compute_weekly_route_metrics


def test_weekly_metrics_basic_calculation():
    # Create dummy shipments for 1 route across 2 weeks
    data = [
        # Week 1: 2024-01-01 (Monday)
        {
            'shipment_id': 'S1', 'origin': 'A', 'destination': 'B', 'route_type': 'Short',
            'material': 'Cement', 'quantity_tonnes': 10.0, 'distance_km': 100.0,
            'freight_cost_inr': 3000.0, 'shipment_date': '2024-01-01', 'transporter': 'T1'
        },
        # Week 2: 2024-01-08 (Monday)
        {
            'shipment_id': 'S2', 'origin': 'A', 'destination': 'B', 'route_type': 'Short',
            'material': 'Cement', 'quantity_tonnes': 10.0, 'distance_km': 100.0,
            'freight_cost_inr': 3600.0, 'shipment_date': '2024-01-08', 'transporter': 'T1'
        }
    ]
    df = pd.DataFrame(data)
    metrics = compute_weekly_route_metrics(df)

    assert len(metrics) == 2
    # Week 1 CPTK = 3000 / (10 * 100) = 3.0
    assert metrics.loc[0, 'cost_per_tonne_km'] == pytest.approx(3.0)
    assert np.isnan(metrics.loc[0, 'own_history_baseline'])
    assert np.isnan(metrics.loc[0, 'vs_own_history_pct'])

    # Week 2 CPTK = 3600 / (10 * 100) = 3.6
    assert metrics.loc[1, 'cost_per_tonne_km'] == pytest.approx(3.6)
    # Own history baseline = 3.0
    assert metrics.loc[1, 'own_history_baseline'] == pytest.approx(3.0)
    # Deviation = (3.6 - 3.0) / 3.0 = +0.20 (+20%)
    assert metrics.loc[1, 'vs_own_history_pct'] == pytest.approx(0.20)


def test_peer_baseline_calculation():
    # Two routes of type 'Short' in the same week
    data = [
        {
            'shipment_id': 'S1', 'origin': 'A', 'destination': 'B', 'route_type': 'Short',
            'material': 'Cement', 'quantity_tonnes': 10.0, 'distance_km': 100.0,
            'freight_cost_inr': 3000.0, 'shipment_date': '2024-01-01', 'transporter': 'T1'
        },
        {
            'shipment_id': 'S2', 'origin': 'C', 'destination': 'D', 'route_type': 'Short',
            'material': 'Cement', 'quantity_tonnes': 10.0, 'distance_km': 100.0,
            'freight_cost_inr': 4000.0, 'shipment_date': '2024-01-01', 'transporter': 'T2'
        }
    ]
    df = pd.DataFrame(data)
    metrics = compute_weekly_route_metrics(df)

    ab_row = metrics[metrics['route'] == 'A-B'].iloc[0]
    cd_row = metrics[metrics['route'] == 'C-D'].iloc[0]

    # A-B CPTK = 3.0, peer (C-D) = 4.0 -> vs peer = (3.0 - 4.0)/4.0 = -0.25 (-25%)
    assert ab_row['peer_baseline'] == pytest.approx(4.0)
    assert ab_row['vs_similar_routes_pct'] == pytest.approx(-0.25)

    # C-D CPTK = 4.0, peer (A-B) = 3.0 -> vs peer = (4.0 - 3.0)/3.0 = +0.3333 (+33.33%)
    assert cd_row['peer_baseline'] == pytest.approx(3.0)
    assert cd_row['vs_similar_routes_pct'] == pytest.approx(1.0 / 3.0)
