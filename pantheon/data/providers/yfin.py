"""Yahoo Finance provider (no API key).

Category functions return formatted strings (CSV/markdown) — the LLM reads
prose. Prices/indicators/fundamentals/news all come from yfinance; indicators
are computed from the price history with stockstats.
"""

from __future__ import annotations

from pantheon.data.errors import NoData, RateLimit


def _history(ticker: str, start_date: str, end_date: str):
    import yfinance as yf
    try:
        df = yf.Ticker(ticker).history(start=start_date, end=end_date, auto_adjust=True)
    except Exception as exc:  # noqa: BLE001 — normalize to our taxonomy
        if "rate" in str(exc).lower() or "429" in str(exc):
            raise RateLimit(f"yfinance throttled for {ticker}") from exc
        raise NoData(f"yfinance error for {ticker}: {exc}") from exc
    if df is None or df.empty:
        raise NoData(f"no yfinance rows for {ticker} in {start_date}..{end_date}")
    return df


def stock(ticker: str, start_date: str, end_date: str) -> str:
    df = _history(ticker, start_date, end_date)
    first, last = float(df["Close"].iloc[0]), float(df["Close"].iloc[-1])
    ret = (last - first) / first * 100 if first else 0.0
    tail = df[["Open", "High", "Low", "Close", "Volume"]].tail(10)
    return (
        f"# Price data for {ticker} ({start_date} → {end_date})\n"
        f"Start {first:.2f} → End {last:.2f} ({ret:+.1f}%). Last 10 sessions (CSV):\n"
        + tail.to_csv()
    )


def indicators(ticker: str, curr_date: str, lookback_days: int = 120) -> str:
    from datetime import datetime, timedelta
    end = datetime.strptime(curr_date, "%Y-%m-%d")
    start = (end - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    df = _history(ticker, start, curr_date)
    try:
        from stockstats import wrap
        s = wrap(df.copy())
        rsi = float(s["rsi_14"].iloc[-1])
        macd = float(s["macd"].iloc[-1])
        macds = float(s["macds"].iloc[-1])
        sma50 = float(s["close_50_sma"].iloc[-1])
        sma200 = float(s["close_200_sma"].iloc[-1]) if len(df) >= 200 else float("nan")
    except Exception as exc:  # noqa: BLE001
        raise NoData(f"indicator computation failed for {ticker}: {exc}") from exc
    return (
        f"# Technical indicators for {ticker} @ {curr_date}\n"
        f"RSI(14): {rsi:.0f} ({'overbought' if rsi > 70 else 'neutral' if rsi > 40 else 'oversold'})\n"
        f"MACD: {macd:.2f} vs signal {macds:.2f} ({'bullish' if macd > macds else 'bearish'})\n"
        f"Close vs SMA50 {sma50:.2f} / SMA200 {sma200:.2f}"
    )


def fundamentals(ticker: str, curr_date: str) -> str:
    import yfinance as yf
    try:
        info = yf.Ticker(ticker).info or {}
    except Exception as exc:  # noqa: BLE001
        raise NoData(f"yfinance fundamentals error for {ticker}: {exc}") from exc
    if not info:
        raise NoData(f"no fundamentals for {ticker}")
    keys = [
        ("marketCap", "Market cap"), ("trailingPE", "Trailing P/E"),
        ("forwardPE", "Forward P/E"), ("profitMargins", "Profit margin"),
        ("revenueGrowth", "Revenue growth"), ("debtToEquity", "Debt/Equity"),
        ("beta", "Beta"),
    ]
    lines = [f"- {label}: {info[k]}" for k, label in keys if info.get(k) is not None]
    return f"# Fundamentals for {ticker} @ {curr_date}\n" + "\n".join(lines or ["- (sparse data)"])


def news(ticker: str, curr_date: str, limit: int = 10) -> str:
    import yfinance as yf
    try:
        items = yf.Ticker(ticker).news or []
    except Exception as exc:  # noqa: BLE001
        raise NoData(f"yfinance news error for {ticker}: {exc}") from exc
    if not items:
        raise NoData(f"no news for {ticker}")
    lines = []
    for it in items[:limit]:
        content = it.get("content", it)
        title = content.get("title") if isinstance(content, dict) else it.get("title")
        if title:
            lines.append(f"- {title}")
    return f"# Recent news for {ticker} @ {curr_date}\n" + "\n".join(lines or ["- (no headlines)"])
