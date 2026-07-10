"""Social sentiment providers: StockTwits and Reddit (both keyless)."""

from __future__ import annotations

from pantheon.data.errors import NoData

_UA = {"User-Agent": "pantheon/0.1 (research)"}


def stocktwits(ticker: str, curr_date: str, limit: int = 25) -> str:
    import requests

    try:
        r = requests.get(f"https://api.stocktwits.com/api/2/streams/symbol/{ticker}.json",
                         headers=_UA, timeout=20)
        r.raise_for_status()
        msgs = r.json().get("messages", [])
    except Exception as exc:  # noqa: BLE001
        raise NoData(f"stocktwits error for {ticker}: {exc}") from exc
    if not msgs:
        raise NoData(f"no stocktwits messages for {ticker}")

    bull = bear = 0
    sample = []
    for m in msgs[:limit]:
        s = ((m.get("entities") or {}).get("sentiment") or {}).get("basic")
        if s == "Bullish":
            bull += 1
        elif s == "Bearish":
            bear += 1
        if len(sample) < 5 and m.get("body"):
            sample.append(f"  · {m['body'][:100]}")
    return (
        f"# StockTwits sentiment for {ticker} @ {curr_date}\n"
        f"Labeled: {bull} bullish / {bear} bearish (of {len(msgs[:limit])} recent).\n"
        + "\n".join(sample)
    )


def reddit(ticker: str, curr_date: str, limit: int = 10) -> str:
    """Reddit search via the public JSON endpoint (no auth)."""
    import requests

    try:
        r = requests.get(
            "https://www.reddit.com/search.json",
            params={"q": ticker, "sort": "new", "limit": limit, "restrict_sr": False},
            headers=_UA, timeout=20,
        )
        r.raise_for_status()
        children = r.json().get("data", {}).get("children", [])
    except Exception as exc:  # noqa: BLE001
        raise NoData(f"reddit error for {ticker}: {exc}") from exc
    posts = [c["data"].get("title") for c in children if c.get("data", {}).get("title")]
    if not posts:
        raise NoData(f"no reddit posts for {ticker}")
    return f"# Reddit chatter for {ticker} @ {curr_date}\n" + "\n".join(f"- {p}" for p in posts[:limit])
