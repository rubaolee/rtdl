#!/usr/bin/env python3
"""Strip review-identifying and nondeterministic metadata from the CGO PDF."""

from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter


TITLE = "Whole-Protocol Admission for Repurposed Ray-Tracing Programs"
FORBIDDEN = (
    b"Lestat",
    b"C:\\Users\\",
    b"C:/Users/",
    b"history/internal_docs",
    b"root@",
    b"192.168.",
    b"213.173.",
    b"157.157.",
    b"codex/v4",
)


def build(raw: bytes) -> bytes:
    reader = PdfReader(BytesIO(raw), strict=True)
    writer = PdfWriter(clone_from=reader)
    writer.xmp_metadata = None
    writer.metadata = {
        "/Title": TITLE,
        "/Author": "Anonymous Author(s)",
    }
    writer._ID = None
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    raw = args.input.read_bytes()
    before = PdfReader(BytesIO(raw), strict=True)
    sanitized = build(raw)
    assert sanitized == build(raw), "sanitizer output is not byte deterministic"
    after = PdfReader(BytesIO(sanitized), strict=True)

    assert len(before.pages) == len(after.pages)
    assert [page.extract_text() for page in before.pages] == [
        page.extract_text() for page in after.pages]
    assert after.xmp_metadata is None
    assert "/ID" not in after.trailer
    metadata = dict(after.metadata or {})
    assert metadata == {"/Title": TITLE, "/Author": "Anonymous Author(s)"}
    for key in ("/CreationDate", "/ModDate", "/Creator", "/Producer"):
        assert key not in metadata
    for value in FORBIDDEN:
        assert value not in sanitized, value

    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_name(args.output.name + ".sanitized-tmp")
    temporary.write_bytes(sanitized)
    temporary.replace(args.output)
    print(f"pages={len(after.pages)}")
    print(f"bytes={len(sanitized)}")
    print(f"sha256={hashlib.sha256(sanitized).hexdigest()}")
    print("xmp_metadata=false")
    print("trailer_id=false")
    print("text_identical=true")
    print("byte_deterministic=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
