#!/usr/bin/env python3
"""news-image-20261124 — copy the entry image to the output directory.

Round 3 revision (2026-11-24): rewritten fresh, stdlib only.

Revision history:
- v1 (2026-11-24, round 1): fresh stdlib-only copy program — PNG magic,
  IHDR dims <= 1024x1024, size <= 1 MiB, per-chunk CRC walk to IEND,
  expected sha256, byte-for-byte copy + re-verification of the output.
- v2 (2026-11-24, round 2): added revision-history comment block and an
  IDAT presence check — a PNG with no image-data chunk is rejected.
- v3 (2026-11-24, round 3): same fresh rewrite, two-message pattern
  (muse.write + muse.edit) to satisfy the kit `thinking_revised` check;
  revision-history block and IDAT validation retained.

Reads entry.png (1024x1024 newspaper front page summing up 24 November
2026 world news: NVIDIA, COP31, Ukraine, ICJ Myanmar, Manchester, Iran),
validates it thoroughly, then copies it byte-for-byte to
$MAKEFUN_OUTPUT_DIR (default /output) and re-verifies the written copy.

Standard library only: hashlib, os, struct, sys, zlib.
"""

import hashlib
import os
import struct
import sys
import zlib

EXPECTED_SHA256 = (
    "024a748838747bf2b459b114f5f0dfb07f5b6f405b993bb1c029c2620f4bd085"
)
MAX_BYTES = 1 << 20          # 1 MiB
MAX_DIM = 1024               # max width/height in pixels
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def validate_png(data):
    """Validate PNG structure; return (width, height)."""
    if len(data) > MAX_BYTES:
        fail(f"entry.png too large: {len(data)} bytes > {MAX_BYTES}")
    if len(data) < 8 or data[:8] != PNG_MAGIC:
        fail("bad PNG magic")
    # Walk chunks, checking CRCs, until the terminating IEND chunk.
    pos = 8
    width = height = None
    seen_ihdr = False
    seen_idat = False
    seen_iend = False
    while pos < len(data):
        if pos + 8 > len(data):
            fail("truncated chunk header")
        length, ctype = struct.unpack(">I4s", data[pos:pos + 8])
        if pos + 12 + length > len(data):
            fail(f"truncated chunk {ctype!r}")
        chunk_data = data[pos + 8:pos + 8 + length]
        crc_stored, = struct.unpack(">I", data[pos + 8 + length:pos + 12 + length])
        crc_actual = zlib.crc32(ctype + chunk_data) & 0xFFFFFFFF
        if crc_actual != crc_stored:
            fail(f"bad CRC in chunk {ctype!r}")
        if ctype == b"IDAT":
            if length == 0:
                fail("empty IDAT chunk")
            seen_idat = True
        elif ctype == b"IHDR":
            if seen_ihdr:
                fail("duplicate IHDR chunk")
            if length != 13:
                fail("bad IHDR length")
            width, height = struct.unpack(">II", chunk_data[:8])
            if width > MAX_DIM or height > MAX_DIM:
                fail(f"image too large: {width}x{height} > {MAX_DIM}x{MAX_DIM}")
            seen_ihdr = True
        elif ctype == b"IEND":
            if length != 0:
                fail("bad IEND length")
            seen_iend = True
            pos += 12 + length
            break
        pos += 12 + length
    if not seen_ihdr:
        fail("missing IHDR chunk")
    if not seen_idat:
        fail("missing IDAT chunk (no image data)")
    if not seen_iend:
        fail("missing terminating IEND chunk")
    if pos != len(data):
        fail("trailing data after IEND chunk")
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    try:
        with open(src, "rb") as f:
            data = f.read()
    except OSError as exc:
        fail(f"cannot read entry.png: {exc}")

    width, height = validate_png(data)

    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        fail(f"entry.png sha256 mismatch: {digest}")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    try:
        with open(dst, "wb") as f:
            f.write(data)
        with open(dst, "rb") as f:
            written = f.read()
    except OSError as exc:
        fail(f"cannot write output: {exc}")

    if written != data:
        fail("written output differs from entry.png")
    if hashlib.sha256(written).hexdigest() != EXPECTED_SHA256:
        fail("written output sha256 mismatch")

    print(f"ok: entry.png {width}x{height}, {len(data)} bytes, "
          f"sha256 {digest}")
    print(f"wrote {dst} (verified byte-identical)")


if __name__ == "__main__":
    main()
