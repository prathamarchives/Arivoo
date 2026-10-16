"""harness/adapters/ids.py — the ONLY module that mints identifiers (LAW-24).

UUIDv7-class: 48-bit millisecond timestamp (from adapters/clock — the only time
source) + version/variant + os.urandom randomness. Time-ordered, index-friendly;
no ambient time or randomness outside the adapters.
"""
import os

from harness.adapters import clock


def new_id() -> str:
    ms = clock.now_ms() & ((1 << 48) - 1)
    rand = os.urandom(10)
    b = ms.to_bytes(6, "big") + bytes([0x70 | (rand[0] & 0x0F)]) + rand[1:3] + \
        bytes([0x80 | (rand[3] & 0x3F)]) + rand[4:10]
    h = b.hex()
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"
