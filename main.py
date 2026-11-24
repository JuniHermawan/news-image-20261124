#!/usr/bin/env python3
"""Copy the entry image to the output directory.

Entry for make.fun competition news-image-20261124: "Sum up 24 November's
world news in one image". The image (entry.png, drawn at build time) is
validated and copied byte-for-byte to /output/entry.png (or to the directory
named by MAKEFUN_OUTPUT_DIR when set). Python 3.13 standard library only;
no third-party packages, no network.

Validation: PNG magic bytes, IHDR chunk with width/height at most
1024x1024, total size at most 1 MiB, a terminating IEND chunk, and a
SHA-256 digest matching the image committed in this repository. The written
copy is re-read and its digest checked again, so both grader runs produce
identical bytes.
"""

import hashlib
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")

# SHA-256 of entry.png as committed in this repository.
EXPECTED_SHA256 = "024a748838747bf2b459b114f5f0dfb07f5b6f405b993bb1c029c2620f4bd085"

MAX_BYTES = 1048576
MAX_DIMENSION = 1024

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
IEND_CHUNK = b"\x00\x00\x00\x00IEND\xaeB`\x82"


def fail(message):
    print("error: " + message, file=sys.stderr)
    sys.exit(1)


def main():
    try:
        with open(SOURCE, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        fail("cannot read entry.png: %s" % exc)

    if len(data) < 33:
        fail("entry.png is too short to be a PNG")
    if data[:8] != PNG_MAGIC:
        fail("entry.png does not start with the PNG magic bytes")
    if data[12:16] != b"IHDR":
        fail("entry.png has no IHDR chunk where one is expected")

    width, height = struct.unpack(">II", data[16:24])
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        fail("image is %dx%d, larger than the 1024x1024 limit" % (width, height))
    if len(data) > MAX_BYTES:
        fail("image is %d bytes, larger than the 1 MiB limit" % len(data))
    if data[-len(IEND_CHUNK):] != IEND_CHUNK:
        fail("entry.png does not end with a complete IEND chunk")

    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA256:
        fail("entry.png sha256 mismatch: got %s" % digest)

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "entry.png")
        with open(out_path, "wb") as handle:
            handle.write(data)
        with open(out_path, "rb") as handle:
            written = handle.read()
    except OSError as exc:
        fail("cannot write output: %s" % exc)

    if hashlib.sha256(written).hexdigest() != EXPECTED_SHA256:
        fail("written copy failed its sha256 check")

    print("wrote %s (%dx%d, %d bytes, sha256 %s)"
          % (out_path, width, height, len(data), digest))


if __name__ == "__main__":
    main()
