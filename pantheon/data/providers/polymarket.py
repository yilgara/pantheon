"""Polymarket prediction-market probabilities (keyless public API)."""

from __future__ import annotations

from pantheon.data.errors import NoData

GAMMA = "https://gamma-api.polymarket.com"


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
            q = m.get("question")
            outcomes = m.get("outcomes")
            prices = m.get("outcomePrices")
            if q and outcomes and prices:
                try:
                    prob = float(prices[0]) if isinstance(prices, list) else float(str(prices).strip("[]").split(",")[0])
                    lines.append(f"- {q} — {prob:.0%}")
                except Exception:  # noqa: BLE001
                    continue
            if len(lines) >= limit:
                break
        if len(lines) >= limit:
            break

    if not lines:
        raise NoData(f"no open prediction markets for {topic!r}")
    return f"# Prediction markets for '{topic}'\n" + "\n".join(lines)
