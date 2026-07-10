"""Data router.

Single entry point between agent tools and providers. For a category, it tries
the configured vendor first, then fallbacks, translating our error taxonomy into
vendor-skipping. Optional categories degrade to a sentinel string instead of
raising, so a missing macro feed never aborts a run.
"""

from __future__ import annotations

import logging
from typing import Callable

from pantheon.config import get_config
from pantheon.data.cache import cached_text
from pantheon.data.errors import NoData, NotConfigured, RateLimit, VendorError
from pantheon.data.providers import alpha_vantage as av
from pantheon.data.providers import fred, mock, polymarket, social, yfin

logger = logging.getLogger(__name__)

# category -> vendor -> callable(key, *args)
_REGISTRY: dict[str, dict[str, Callable]] = {
    "stock":        {"yfinance": yfin.stock,        "alpha_vantage": av.stock,        "mock": mock.stock},
    "indicators":   {"yfinance": yfin.indicators,   "mock": mock.indicators},
    "fundamentals": {"yfinance": yfin.fundamentals, "alpha_vantage": av.fundamentals, "mock": mock.fundamentals},
    "news":         {"yfinance": yfin.news,         "alpha_vantage": av.news,         "mock": mock.news},
    "social":       {"stocktwits": social.stocktwits, "reddit": social.reddit,        "mock": mock.social},
    "macro":        {"fred": fred.macro,             "mock": mock.macro},
    "prediction_markets": {"polymarket": polymarket.prediction_markets,               "mock": mock.prediction_markets},
}

# Ordered fallbacks after the configured primary vendor (mock is always last).
_FALLBACKS: dict[str, list[str]] = {
    "stock": ["alpha_vantage", "mock"], "indicators": ["mock"],
    "fundamentals": ["alpha_vantage", "mock"], "news": ["alpha_vantage", "mock"],
    "social": ["reddit", "mock"], "macro": ["mock"], "prediction_markets": ["mock"],
}


def _vendor_chain(category: str) -> list[str]:
    cfg = get_config()
    primary = cfg["data_vendors"].get(category)
    chain = ([primary] if primary else []) + _FALLBACKS.get(category, [])
    # de-dup, keep only vendors we actually have registered
    seen, out = set(), []
    for v in chain:
        if v in _REGISTRY.get(category, {}) and v not in seen:
            seen.add(v); out.append(v)
    return out


def get(category: str, ticker: str, *args, use_cache: bool = True) -> str:
    """Fetch `category` data for `ticker`, trying vendors in order."""
    cfg = get_config()
    chain = _vendor_chain(category)

    if not chain:
        msg = f"NO_DATA_AVAILABLE: category '{category}' has no usable vendor"
        if category in cfg["optional_categories"]:
            return msg
        raise NotConfigured(msg)

    first_error: Exception | None = None
    for vendor in chain:
        fn = _REGISTRY[category][vendor]
        params = f"{vendor}|{'|'.join(map(str, args))}"
        try:
            if use_cache:
                return cached_text(category, ticker, params, lambda: fn(ticker, *args))
            return fn(ticker, *args)
        except (RateLimit, NotConfigured) as exc:
            logger.warning("router: %s/%s skipped (%s)", category, vendor, exc)
            first_error = first_error or exc
        except (NoData, VendorError) as exc:
            logger.warning("router: %s/%s no data (%s)", category, vendor, exc)
            first_error = first_error or exc

    # all vendors failed
    if category in cfg["optional_categories"]:
        return f"DATA_UNAVAILABLE: {category} for {ticker} ({first_error})"
    raise first_error or NoData(f"no data for {category}/{ticker}")
