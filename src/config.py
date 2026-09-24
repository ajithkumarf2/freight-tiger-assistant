"""
Configuration module for FreightTiger Shipping Cost Assistant.
"""

import os

# Implementation Assumption: Anomaly Flagging Threshold.
# Note: 20% (0.20) is NOT an explicitly confirmed FreightTiger requirement,
# but an implementation assumption inferred from the sample output examples.
# The threshold remains configurable here.
ANOMALY_THRESHOLD = float(os.getenv("ANOMALY_THRESHOLD", "0.20"))

# LLM Model Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.0"))
