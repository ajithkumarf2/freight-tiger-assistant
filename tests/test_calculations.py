"""
Test suite wrapper for calculations module.
Re-exports metrics engine unit tests.
"""

from tests.test_metrics_engine import (
    test_weekly_metrics_basic_calculation,
    test_peer_baseline_calculation
)
