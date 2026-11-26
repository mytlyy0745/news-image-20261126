#!/usr/bin/env python3
"""Entrypoint for news-image-20261126.

Validates the entry image shipped in this repository (entry.png) and copies
it byte-identical to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).

Validation is strict: PNG magic, file size, IHDR dimensions 1024x1024,
bit depth 8 / colour type 2 (truecolour RGB), a CRC check on every chunk,
and a trailing IEND chunk as the last 12 bytes. Any failure exits non-zero
and writes nothing.
"""
import os
import struct
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
MAX_BYTES = 1048576
EXPECT_W, EXPECT_H = 1024, 1024

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def fail(msg):
    print("main.py: refusing entry.png: %s" % msg, file=sys.stderr)
    return 1


def validate(data):
    if len(data) > MAX_BYTES:
        return "file is %d bytes, over the 1 MiB cap" % len(data)
    if len(data) < 8 or data[:8] != PNG_MAGIC:
        return "missing PNG magic"
    # Walk chunks: length (4) + type (4) + data + CRC (4).
    pos = 8
    seen_ihdr = False
    seen_iend = False
    while pos < len(data):
        if pos + 8 > len(data):
            return "truncated chunk header at offset %d" % pos
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        end = pos + 8 + length + 4
        if end > len(data):
            return "truncated %s chunk at offset %d" % (ctype.decode("latin1"), pos)
        chunk_data = data[pos + 8:pos + 8 + length]
        crc_stored = struct.unpack(">I", data[pos + 8 + length:end])[0]
        crc_actual = zlib.crc32(ctype + chunk_data) & 0xFFFFFFFF
        if crc_stored != crc_actual:
            return "bad CRC in %s chunk" % ctype.decode("latin1")
        if ctype == b"IHDR":
            if seen_ihdr:
                return "duplicate IHDR"
            seen_ihdr = True
            if length != 13:
                return "IHDR is %d bytes, expected 13" % length
            w, h, depth, ctype_no, comp, filt, inter = struct.unpack(
                ">IIBBBBB", chunk_data)
            if (w, h) != (EXPECT_W, EXPECT_H):
                return "image is %dx%d, expected 1024x1024" % (w, h)
            if depth != 8 or ctype_no != 2:
                return ("unsupported bit depth %d / colour type %d "
                        "(expected 8 / 2)" % (depth, ctype_no))
            if comp != 0 or filt != 0 or inter != 0:
                return "unsupported compression/filter/interlace in IHDR"
        if ctype == b"IEND":
            seen_iend = True
            if end != len(data):
                return "trailing bytes after IEND"
            break
        pos = end
    if not seen_ihdr:
        return "no IHDR chunk"
    if not seen_iend:
        return "no trailing IEND chunk"
    return None


def main():
    try:
        with open(SRC, "rb") as f:
            data = f.read()
    except OSError as e:
        print("main.py: cannot read entry.png: %s" % e, file=sys.stderr)
        return 1
    err = validate(data)
    if err:
        return fail(err)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "entry.png")
        with open(out_path, "wb") as f:
            f.write(data)
        with open(out_path, "rb") as f:
            written = f.read()
    except OSError as e:
        print("main.py: cannot write output: %s" % e, file=sys.stderr)
        return 1
    if written != data:
        return fail("output bytes differ from entry.png")
    print("main.py: wrote %s (%d bytes, sha256 %s)"
          % (out_path, len(data),
             __import__("hashlib").sha256(data).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
