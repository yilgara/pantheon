"""LLM-callable data tools.

Thin `@tool` wrappers over the data router. The docstring/annotations become
the tool description the model sees, so keep them clear. Analysts bind the
subset relevant to their modality.
"""

from __future__ import annotations

from typing import Annotated

from langchain_core.tools import tool

from pantheon.data import router


@tool
def get_stock_data(
    ticker: Annotated[str, "Ticker symbol, e.g. NVDA"],
    start_date: Annotated[str, "Start date, yyyy-mm-dd"],
    end_date: Annotated[str, "End date, yyyy-mm-dd"],
) -> str:
    """Daily OHLCV price history and period return for a stock."""
    return router.get("stock", ticker, start_date, end_date)


@tool
def get_indicators(
    ticker: Annotated[str, "Ticker symbol, e.g. NVDA"],
    curr_date: Annotated[str, "As-of date, yyyy-mm-dd"],
) -> str:
    """Technical indicators (RSI, MACD, moving averages) as of a date."""
    return router.get("indicators", ticker, curr_date)


@tool
def get_fundamentals(
    ticker: Annotated[str, "Ticker symbol, e.g. NVDA"],
    curr_date: Annotated[str, "As-of date, yyyy-mm-dd"],
) -> str:
    """Company fundamentals: valuation, margins, growth, leverage."""
    return router.get("fundamentals", ticker, curr_date)


@tool
def get_news(
    ticker: Annotated[str, "Ticker symbol, e.g. NVDA"],
    curr_date: Annotated[str, "As-of date, yyyy-mm-dd"],
) -> str:
    """Recent news headlines relevant to the ticker."""
    return router.get("news", ticker, curr_date)


# Convenient groupings for each analyst's tool binding.
MARKET_TOOLS = [get_stock_data, get_indicators]
FUNDAMENTALS_TOOLS = [get_fundamentals]
NEWS_TOOLS = [get_news]
SOCIAL_TOOLS = [get_news]  # v1: reuse news as the social/sentiment signal
