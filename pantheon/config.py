"""Central configuration.

A single DEFAULT_CONFIG dict, overridable via environment variables (PANTHEON_*)
and via set_config() at runtime. Mirrors the reference approach: data-vendor
selection per category, a disk cache location, LLM settings, and debate-round
limits — kept lean for v1.
"""

from __future__ import annotations

import os
from copy import deepcopy
from typing import Any

_HOME = os.getenv("PANTHEON_HOME", os.path.join(os.path.expanduser("~"), ".pantheon"))

DEFAULT_CONFIG: dict[str, Any] = {
    # ---- LLM (provider-agnostic; resolved by pantheon/llm.py) ----
    "llm_provider": os.getenv("PANTHEON_LLM_PROVIDER", "openai"),
    "deep_think_llm": os.getenv("PANTHEON_DEEP_THINK_LLM", "gpt-4o"),
    "quick_think_llm": os.getenv("PANTHEON_QUICK_THINK_LLM", "gpt-4o-mini"),
    "backend_url": os.getenv("PANTHEON_LLM_BACKEND_URL"),  # e.g. Ollama base URL
    "temperature": float(os.getenv("PANTHEON_TEMPERATURE", "0.7")),
    "llm_max_retries": int(os.getenv("PANTHEON_LLM_MAX_RETRIES", "3")),

    # ---- Data vendors per category (primary; fallbacks live in the router) ----
    "data_vendors": {
        "stock": "yfinance",
        "indicators": "yfinance",
        "fundamentals": "yfinance",
        "news": "yfinance",
        "macro": "fred",
        "prediction_markets": "polymarket",
    },
    # Categories that degrade to a sentinel string on failure instead of aborting.
    "optional_categories": ["macro", "prediction_markets"],

    # ---- Cache ----
    "data_cache_dir": os.getenv("PANTHEON_CACHE_DIR", os.path.join(_HOME, "cache")),

    # ---- Debate control ----
    "max_debate_rounds": int(os.getenv("PANTHEON_MAX_DEBATE_ROUNDS", "1")),
    "max_risk_rounds": int(os.getenv("PANTHEON_MAX_RISK_ROUNDS", "1")),
    "max_recur_limit": int(os.getenv("PANTHEON_MAX_RECUR_LIMIT", "100")),

    # ---- Scanner (Pantheon addition) ----
    "scanner_mode": os.getenv("PANTHEON_SCANNER_MODE", "human"),  # "human" | "agent"
    "scanner_universe": ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META", "TSLA", "AMD"],
}


_config: dict[str, Any] | None = None


def get_config() -> dict[str, Any]:
    """Return the active config (a copy, so callers can't mutate the singleton)."""
    global _config
    if _config is None:
        _config = deepcopy(DEFAULT_CONFIG)
    return deepcopy(_config)


def set_config(overrides: dict[str, Any]) -> None:
    """Merge overrides into the active config (dict values merged one level deep)."""
    global _config
    if _config is None:
        _config = deepcopy(DEFAULT_CONFIG)
    for k, v in overrides.items():
        if isinstance(v, dict) and isinstance(_config.get(k), dict):
            _config[k].update(v)
        else:
            _config[k] = v


def reset_config() -> None:
    """Reset to DEFAULT_CONFIG (mainly for tests)."""
    global _config
    _config = None
