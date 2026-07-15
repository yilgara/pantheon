"""Polymarket prediction-market probabilities (keyless public API)."""

from __future__ import annotations

import json

from pantheon.data.errors import NoData

GAMMA = "https://gamma-api.polymarket.com"


def _as_list(v):
    """Polymarket returns outcomes/prices as JSON-encoded strings; normalize to lists."""
    if isinstance(v, str):
        try:
            return json.loads(v)
        except Exception:  # noqa: BLE001
            return None
    return v


def _is_forward_looking(m: dict) -> bool:
    """Keep only unresolved, future-resolving markets.

    `closed` is the reliable resolved flag (`active` stays True even for settled
    markets), and a past `endDate` means the event already resolved.
    """
    from datetime import datetime, timezone

    if m.get("closed"):
        return False
    end = m.get("endDate")
    if end:
        try:
            if datetime.fromisoformat(end.replace("Z", "+00:00")) < datetime.now(timezone.utc):
                return False
        except (ValueError, AttributeError):
            pass
    return True


def prediction_markets(topic: str, curr_date: str | None = None, limit: int = 6) -> str:
    import requests

    try:
        r = requests.get(f"{GAMMA}/public-search",
                         params={"q": topic, "limit_per_type": 20}, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception as exc:  # noqa: BLE001
        raise NoData(f"polymarket error for {topic!r}: {exc}") from exc

    lines = []
    for event in data.get("events", []):
        for m in event.get("markets", []):
            if not _is_forward_looking(m):
                continue
            q = m.get("question")
            prices = _as_list(m.get("outcomePrices"))
            outcomes = _as_list(m.get("outcomes"))
            if q and prices:
                try:
                    prob = float(prices[0])
                except (TypeError, ValueError):
                    continue
                label = f" ({outcomes[0]})" if outcomes else ""
                lines.append(f"- {q}{label}: {prob:.0%}")
            if len(lines) >= limit:
                break
        if len(lines) >= limit:
            break

    if not lines:
        raise NoData(f"no open prediction markets for {topic!r}")
    return f"# Prediction markets for '{topic}'\n" + "\n".join(lines)
