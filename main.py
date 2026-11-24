#!/usr/bin/env python3
"""news-image-20261124 -- copy the validated entry image to the output dir.

Revision history:
  v1 (2026-11-24): fresh copy program -- PNG magic, IHDR dims, size,
    chunk CRC walk to IEND, expected sha256, byte-for-byte copy with
    re-verification of the written file.
  v2 (2026-11-24): added IDAT presence check -- a PNG with no image
    data chunk is rejected even if its header and IEND are well formed.

The image sums up Tuesday 24 November 2026 in one newspaper front page:
NVIDIA, COP31, Ukraine, ICJ Myanmar, Manchester, Iran -- six stories,
masthead "THE WORLD IN ONE DAY / TUESDAY - 24 NOVEMBER 2026".

Standard library only. The program never draws or alters the image: it
validates the PNG shipped beside it, copies it byte-for-byte to
$MAKEFUN_OUTPUT_DIR (default /output) as entry.png, then re-verifies the
written copy. Deterministic: the same input bytes always produce the
same output bytes.
"""

import hashlib
import os
import struct
import sys
import zlib

EXPECTED_SHA256 = "024a748838747bf2b459b114f5f0dfb07f5b6f405b993bb1c029c2620f4bd085"
MAX_BYTES = 1_048_576
MAX_DIMENSION = 1024
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print("error: " + message, file=sys.stderr)
    raise SystemExit(1)


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def validate_png(data):
    """Check magic, size, IHDR dimensions and that chunks walk to IEND."""
    if len(data) > MAX_BYTES:
        fail("entry.png is %d bytes, over the 1 MiB limit" % len(data))
    if len(data) < 8 or data[:8] != PNG_MAGIC:
        fail("entry.png does not start with the PNG magic bytes")
    offset = 8
    seen_ihdr = False
    seen_idat = False
    seen_iend = False
    while offset + 8 <= len(data):
        length, chunk_type = struct.unpack(">I4s", data[offset:offset + 8])
        body_start = offset + 8
        body_end = body_start + length
        crc_end = body_end + 4
        if crc_end > len(data):
            fail("truncated PNG chunk %r" % chunk_type)
        stored_crc = struct.unpack(">I", data[body_end:crc_end])[0]
        actual_crc = zlib.crc32(chunk_type)
        actual_crc = zlib.crc32(data[body_start:body_end], actual_crc)
        if actual_crc & 0xFFFFFFFF != stored_crc:
            fail("bad CRC in PNG chunk %r" % chunk_type)
        if chunk_type == b"IHDR":
            if seen_ihdr:
                fail("duplicate IHDR chunk")
            if length != 13:
                fail("IHDR chunk is %d bytes, expected 13" % length)
            width, height = struct.unpack(">II", data[body_start:body_start + 8])
            if width == 0 or height == 0:
                fail("IHDR has a zero dimension")
            if width > MAX_DIMENSION or height > MAX_DIMENSION:
                fail("image is %dx%d, over the 1024x1024 limit" % (width, height))
            seen_ihdr = True
        if chunk_type == b"IDAT":
            if length == 0:
                fail("empty IDAT chunk")
            seen_idat = True
        if chunk_type == b"IEND":
            if length != 0:
                fail("IEND chunk is not empty")
            if crc_end != len(data):
                fail("trailing bytes after IEND chunk")
            seen_iend = True
            break
        offset = crc_end
    if not seen_ihdr:
        fail("no IHDR chunk found")
    if not seen_idat:
        fail("no IDAT chunk found")
    if not seen_iend:
        fail("no terminating IEND chunk found")


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    try:
        with open(source, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        fail("cannot read entry.png: %s" % exc)
    validate_png(data)
    digest = sha256_hex(data)
    if digest != EXPECTED_SHA256:
        fail("entry.png sha256 mismatch: got %s" % digest)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(out_dir, exist_ok=True)
        target = os.path.join(out_dir, "entry.png")
        with open(target, "wb") as handle:
            handle.write(data)
        with open(target, "rb") as handle:
            written = handle.read()
    except OSError as exc:
        fail("cannot write output: %s" % exc)
    if sha256_hex(written) != EXPECTED_SHA256:
        fail("written entry.png failed re-verification")
    print("ok: wrote %s (%d bytes, sha256 %s)" % (target, len(written), EXPECTED_SHA256))
    return 0


if __name__ == "__main__":
    sys.exit(main())
