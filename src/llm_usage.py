"""
Token and Cost Logging Utility for FreightTiger Shipping Cost Assistant.

Tracks LLM calls, input tokens, output tokens, total tokens, and estimated cost in USD.
"""

import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any


# Model pricing per 1,000,000 tokens (USD)
# Source: Published rates for OpenAI models
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4o-mini": {
        "input_per_1m": 0.150,   # $0.15 per 1M input tokens
        "output_per_1m": 0.600,  # $0.60 per 1M output tokens
    },
    "gpt-4o": {
        "input_per_1m": 2.50,    # $2.50 per 1M input tokens
        "output_per_1m": 10.00,  # $10.00 per 1M output tokens
    },
    "gpt-3.5-turbo": {
        "input_per_1m": 0.50,
        "output_per_1m": 1.50,
    }
}


class LLMUsageTracker:
    """
    Singleton-style tracker for logging LLM token counts and costs across runs.
    """

    def __init__(self):
        self.logs: List[Dict[str, Any]] = []

    def log_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        custom_cost: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Records an LLM call event and calculates cost based on published rates.
        """
        total_tokens = input_tokens + output_tokens
        
        # Calculate cost
        estimated_cost = custom_cost
        if estimated_cost is None and model in MODEL_PRICING:
            p = MODEL_PRICING[model]
            in_cost = (input_tokens / 1_000_000.0) * p["input_per_1m"]
            out_cost = (output_tokens / 1_000_000.0) * p["output_per_1m"]
            estimated_cost = in_cost + out_cost

        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(estimated_cost, 6) if estimated_cost is not None else None
        }

        self.logs.append(entry)
        return entry

    def get_summary(self) -> Dict[str, Any]:
        """
        Returns an aggregate summary of all recorded LLM calls.
        """
        total_calls = len(self.logs)
        total_input = sum(l["input_tokens"] for l in self.logs)
        total_output = sum(l["output_tokens"] for l in self.logs)
        total_tokens = sum(l["total_tokens"] for l in self.logs)
        
        costs = [l["estimated_cost_usd"] for l in self.logs if l["estimated_cost_usd"] is not None]
        total_cost = sum(costs) if costs else 0.0

        return {
            "total_llm_calls": total_calls,
            "total_input_tokens": total_input,
            "total_output_tokens": total_output,
            "total_tokens": total_tokens,
            "total_estimated_cost_usd": round(total_cost, 6),
            "logs": self.logs
        }

    def reset(self):
        """
        Resets log history (useful for unit tests).
        """
        self.logs = []


# Global usage tracker instance
usage_tracker = LLMUsageTracker()
