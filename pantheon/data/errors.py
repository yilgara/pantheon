"""Vendor error taxonomy.

Three router-visible error types drive vendor-agnostic fallback: a vendor that
is throttled, one that is missing its key, or one that genuinely has no data.
"""

from __future__ import annotations


class VendorError(Exception):
    """Base: a vendor could not return usable data."""


class NoData(VendorError):
    """Vendor returned nothing usable (empty or stale)."""


class RateLimit(VendorError):
    """Vendor throttled the request; the router should try the next vendor."""


class NotConfigured(VendorError):
    """Vendor selected but not usable here (missing key / not implemented)."""
