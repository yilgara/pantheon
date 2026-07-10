"""FRED macro data (Federal Reserve). Needs a free FRED_API_KEY; degrades if absent."""

from __future__ import annotations

import os

from pantheon.data.errors import NoData, NotConfigured

FRED_BASE = "https://api.stlouisfed.org/fred"

# A small curated set for macro context (alias -> FRED series id).
SERIES = {
    "Fed funds rate": "FEDFUNDS",
    "CPI (inflation)": "CPIAUCSL",
    "10Y Treasury": "DGS10",
    "Unemployment": "UNRATE",
}


def macro(topic: str, curr_date: str) -> str:
    key = os.getenv("FRED_API_KEY")
    if not key:
        raise NotConfigured("FRED_API_KEY not set")
    import requests

    lines = [f"# Macro backdrop @ {curr_date} (FRED)"]
    got_any = False
    for label, sid in SERIES.items():
        try:
            r = requests.get(
                f"{FRED_BASE}/series/observations",
                params={"series_id": sid, "api_key": key, "file_type": "json",
                        "observation_end": curr_date, "sort_order": "desc", "limit": 1},
                timeout=20,
            )
            r.raise_for_status()
            obs = r.json().get("observations", [])
            if obs and obs[0].get("value") not in (".", None):
                lines.append(f"- {label}: {obs[0]['value']} (as of {obs[0]['date']})")
                got_any = True
        except Exception:  # noqa: BLE001 — one bad series shouldn't sink the rest
            continue
    if not got_any:
        raise NoData("FRED returned no usable observations")
    return "\n".join(lines)
