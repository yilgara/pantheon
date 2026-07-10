"""Alpha Vantage provider — fallback vendor for stock / fundamentals / news.

Needs a free ALPHA_VANTAGE_API_KEY; degrades (NotConfigured) if absent so the
router moves on. Free tier is heavily rate-limited, hence fallback-only.
"""

from __future__ import annotations

import os

from pantheon.data.errors import NoData, NotConfigured, RateLimit

BASE = "https://www.alphavantage.co/query"


def _request(function: str, params: dict) -> dict:
    key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not key:
        raise NotConfigured("ALPHA_VANTAGE_API_KEY not set")
    import requests

    q = {"function": function, "apikey": key, **params}
    r = requests.get(BASE, params=q, timeout=30)
    r.raise_for_status()
    data = r.json()
    notice = data.get("Information") or data.get("Note")
    if notice:
        if "rate" in notice.lower() or "limit" in notice.lower():
            raise RateLimit(f"alpha_vantage: {notice[:80]}")
        raise NotConfigured(f"alpha_vantage: {notice[:80]}")
    return data


def stock(ticker: str, start_date: str, end_date: str) -> str:
    data = _request("TIME_SERIES_DAILY", {"symbol": ticker, "outputsize": "compact"})
    series = data.get("Time Series (Daily)", {})
    rows = [(d, v) for d, v in sorted(series.items()) if start_date <= d <= end_date]
    if not rows:
        raise NoData(f"alpha_vantage: no rows for {ticker}")
    first, last = float(rows[0][1]["4. close"]), float(rows[-1][1]["4. close"])
    ret = (last - first) / first * 100 if first else 0.0
    return (f"# Price data for {ticker} ({start_date} → {end_date}) [Alpha Vantage]\n"
            f"Start {first:.2f} → End {last:.2f} ({ret:+.1f}%). {len(rows)} sessions.")


def fundamentals(ticker: str, curr_date: str) -> str:
    data = _request("OVERVIEW", {"symbol": ticker})
    if not data or "Symbol" not in data:
        raise NoData(f"alpha_vantage: no overview for {ticker}")
    keys = [("MarketCapitalization", "Market cap"), ("PERatio", "P/E"),
            ("ProfitMargin", "Profit margin"), ("QuarterlyRevenueGrowthYOY", "Rev growth YoY"),
            ("Beta", "Beta")]
    lines = [f"- {label}: {data[k]}" for k, label in keys if data.get(k)]
    return f"# Fundamentals for {ticker} @ {curr_date} [Alpha Vantage]\n" + "\n".join(lines or ["- (sparse)"])


def news(ticker: str, curr_date: str, limit: int = 10) -> str:
    data = _request("NEWS_SENTIMENT", {"tickers": ticker, "limit": str(limit)})
    feed = data.get("feed", [])
    if not feed:
        raise NoData(f"alpha_vantage: no news for {ticker}")
    lines = [f"- {it.get('title')} ({it.get('overall_sentiment_label','')})" for it in feed[:limit] if it.get("title")]
    return f"# News for {ticker} @ {curr_date} [Alpha Vantage]\n" + "\n".join(lines)
