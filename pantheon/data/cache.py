"""Tiny disk cache for provider results.

Keyed by (namespace, ticker, params) as a CSV/text file under the configured
cache dir. Providers opt in by wrapping a fetch in `cached_text`.
"""

from __future__ import annotations

import hashlib
import os
import re
from typing import Callable

from pantheon.config import get_config

_SAFE = re.compile(r"[^A-Za-z0-9._=-]")


def _safe(component: str, max_len: int = 40) -> str:
    """Make a string safe to use in a filename (guards against path escapes)."""
    cleaned = _SAFE.sub("_", component)[:max_len]
    if set(cleaned) <= {".", "_"}:  # e.g. "..", "."
        cleaned = "x" + cleaned
    return cleaned


def cache_path(namespace: str, ticker: str, params: str) -> str:
    cfg = get_config()
    key = _safe(f"{ticker}-{params}")
    digest = hashlib.sha1(params.encode()).hexdigest()[:8]
    fname = f"{_safe(ticker)}-{namespace}-{key}-{digest}.txt"
    return os.path.join(cfg["data_cache_dir"], _safe(namespace), fname)


def cached_text(namespace: str, ticker: str, params: str, fetch: Callable[[], str]) -> str:
    """Return cached text if present and non-empty, else fetch, store, return."""
    path = cache_path(namespace, ticker, params)
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            data = f.read()
        if data.strip():
            return data
    result = fetch()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(result)
    return result
