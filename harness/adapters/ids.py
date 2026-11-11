"""harness/adapters/ids.py — the ONLY module that mints identifiers (LAW-24).

UUIDv7-class: 48-bit millisecond timestamp (from adapters/clock — the only time
source) + version/variant + os.urandom randomness. Time-ordered, index-friendly;
no ambient time or randomness outside the adapters.
"""
import os
import threading

from harness.adapters import clock

# P3-K0 (the ordering contract): datetime.now() is NOT monotone (NTP steps can
# move it backward), so the mint keeps a process-local floor — a batch of IDs
# is always non-decreasing at ms granularity (the standard v7 monotonicity
# guard; the kernel suite's K-07 caught the raw clock stepping backward live).
_last_ms = 0
_lock = threading.Lock()


def new_id() -> str:
    global _last_ms
    with _lock:
        ms = max(clock.now_ms(), _last_ms) & ((1 << 48) - 1)
        _last_ms = ms
    rand = os.urandom(10)
    # RFC-4122 v7 layout (the P3-K0 repair — the S2-era byte order put the
    # variant byte at index 9; RFC-4122's byte 8 carries the variant bits, so
    # the minted IDs carried invalid variants — caught by the kernel suite's
    # K-07/K-08, red-02.txt):
    #   bytes 0-5   unix_ts_ms (48 bits, big-endian)
    #   byte  6     ver 0b0111 | rand (the version nibble: 7)
    #   byte  7     rand
    #   byte  8     var 0b10 | rand (RFC-4122: the top two bits are 10)
    #   bytes 9-15  rand
    b = ms.to_bytes(6, "big") + bytes([
        0x70 | (rand[0] & 0x0F),
        rand[1],
        0x80 | (rand[2] & 0x3F),
    ]) + rand[3:10]
    h = b.hex()
    return f"{h[0:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def new_agent_token() -> str:
    """P4-E slice one (CLAIM-077): the scoped-agent credential's token VALUE —
    the ONLY secrets-class randomness in the id/adapter layer (LAW-24: ambient
    randomness lives here, never in the command surface). 32 bytes of
    os.urandom, urlsafe-encoded (~190 bits); the FIRST CHARACTER constrained
    to the non-dash range (a leading '_' is argv-safe and occurs) (the F-074-1 class caught live by CLAIM-077's
    own measured set: a leading '-' breaks the separate-argv form
    '--agent-token <value>' at argparse — a property of the generated value,
    never an argv-convention change; the entropy cost 1/64 of the space)."""
    import base64
    while True:
        tok = base64.urlsafe_b64encode(os.urandom(32)).decode("ascii").rstrip("=")
        if tok and tok[0] != "-":
            return tok
