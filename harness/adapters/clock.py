"""harness/adapters/clock.py — the ONLY module that reads ambient time (LAW-24).

Substrate rows take created_at as a PARAMETER from here — never SQL now(), never
datetime.now()/time.time() in any other module (the S4 boundary lint enforces the
class). ids.py is the one permitted consumer of the numeric form.
"""
from datetime import datetime, timezone


def now() -> str:
    """UTC now as an ISO-8601 timestamp string (the INSERT parameter form)."""
    return datetime.now(timezone.utc).isoformat()


def now_ms() -> int:
    """UTC now as epoch milliseconds (consumed by adapters/ids for UUIDv7-class IDs)."""
    return int(datetime.now(timezone.utc).timestamp() * 1000)
