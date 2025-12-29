"""Simple metrics wrapper for Cloud Tasks.

Uses prometheus_client if available; otherwise provides no-op counters to avoid import errors.
"""
import logging

logger = logging.getLogger(__name__)

try:
    from prometheus_client import Counter, Gauge

    balance_sync_success = Counter("mexc_balance_sync_success_total", "Successful balance syncs")
    balance_sync_failure = Counter("mexc_balance_sync_failure_total", "Failed balance syncs")

    price_fetch_success = Counter("mexc_price_fetch_success_total", "Successful price fetches")
    price_fetch_failure = Counter("mexc_price_fetch_failure_total", "Failed price fetches")
    price_missing_count = Counter("mexc_price_missing_total", "Times price was missing from exchange and fallback used")
    last_price_gauge = Gauge("mexc_last_price", "Last known QRL/USDT price")

    reconcile_success = Counter("mexc_reconcile_success_total", "Successful reconcile runs")
    reconcile_insufficient = Counter("mexc_reconcile_insufficient_total", "Reconcile runs with insufficient data")
    reconcile_failure = Counter("mexc_reconcile_failure_total", "Failed reconcile runs")
except Exception as e:
    logger.warning("prometheus_client not available, metrics will be no-op: %s", e)

    class _Noop:
        def inc(self, n: int = 1):
            return None

        def set(self, v):
            return None

    balance_sync_success = _Noop()
    balance_sync_failure = _Noop()
    price_fetch_success = _Noop()
    price_fetch_failure = _Noop()
    price_missing_count = _Noop()
    last_price_gauge = _Noop()
    reconcile_success = _Noop()
    reconcile_insufficient = _Noop()
    reconcile_failure = _Noop()
