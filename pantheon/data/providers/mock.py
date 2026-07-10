"""Offline mock provider.

Deterministic, network-free stand-ins so the whole pipeline runs in tests and
demos without API access. Values vary by ticker (hash-seeded) so different
tickers look different, but a given ticker is always the same.
"""

from __future__ import annotations

import hashlib


def _seed(ticker: str) -> float:
    h = int(hashlib.sha1(ticker.upper().encode()).hexdigest(), 16)
    return (h % 1000) / 1000.0  # 0..1


def stock(ticker: str, start_date: str, end_date: str) -> str:
    s = _seed(ticker)
    ret = round((s - 0.4) * 0.6 * 100, 1)  # -24%..+36%
    return (
        f"# [MOCK] Price data for {ticker} ({start_date} → {end_date})\n"
        f"60-day return: {ret:+.1f}%. Trend: {'up' if ret > 0 else 'down'}. "
        f"Close range roughly {80 + s*40:.0f}–{120 + s*60:.0f}."
    )


def indicators(ticker: str, curr_date: str) -> str:
    s = _seed(ticker)
    rsi = round(40 + s * 45, 0)
    return (
        f"# [MOCK] Technical indicators for {ticker} @ {curr_date}\n"
        f"RSI: {rsi:.0f} ({'overbought' if rsi > 70 else 'neutral' if rsi > 40 else 'oversold'}). "
        f"MACD: {'positive, above signal' if s > 0.4 else 'negative'}. "
        f"50/200 SMA: {'golden cross' if s > 0.5 else 'below'}."
    )


def fundamentals(ticker: str, curr_date: str) -> str:
    s = _seed(ticker)
    return (
        f"# [MOCK] Fundamentals for {ticker} @ {curr_date}\n"
        f"Revenue growth YoY: {round(s*200):d}%. Gross margin: {round(40 + s*40):d}%. "
        f"Fwd P/E: {round(15 + s*40):d}. Balance sheet: {'solid' if s > 0.3 else 'levered'}."
    )


def news(ticker: str, curr_date: str) -> str:
    s = _seed(ticker)
    tone = "positive" if s > 0.55 else "mixed" if s > 0.3 else "cautious"
    return (
        f"# [MOCK] News for {ticker} @ {curr_date}\n"
        f"Overall tone: {tone}. Headlines: demand trends, an upcoming earnings catalyst, "
        f"and no adverse regulatory news."
    )


def social(ticker: str, curr_date: str) -> str:
    s = _seed(ticker)
    bull = round(s * 100)
    return (
        f"# [MOCK] Social sentiment for {ticker} @ {curr_date}\n"
        f"Crowd is {bull}% bullish. Mentions {'rising' if s > 0.5 else 'flat'}; "
        f"{'euphoric FOMO tone (a mild contrarian flag)' if s > 0.7 else 'measured discussion'}."
    )


def macro(topic: str, curr_date: str) -> str:
    return (
        f"# [MOCK] Macro backdrop @ {curr_date}\n"
        "Fed funds ~5.3%, CPI cooling, 10Y ~4.4%, unemployment ~3.9%. "
        "Backdrop neutral-to-supportive for equities."
    )


def prediction_markets(topic: str, curr_date: str | None = None) -> str:
    s = _seed(topic)
    return (
        f"# [MOCK] Prediction markets for '{topic}'\n"
        f"- Positive quarterly outcome — {round(45 + s*40)}%\n"
        f"- Sector outperforms next month — {round(40 + s*30)}%"
    )
