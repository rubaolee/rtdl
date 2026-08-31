"""Verify the Goal5797-A1 single CFR using only that Markdown file."""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path


MANIFEST = re.compile(r"^\| `([^`]+)` \| ([0-9]+) \| `([0-9a-f]{64})` \|$")
HEADING = re.compile(r"^### `([^`]+)`$")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cfr", type=Path)
    args = parser.parse_args()
    raw = args.cfr.read_bytes()
    text = raw.decode("utf-8", errors="strict")
    if "\r" in text:
        raise RuntimeError("CFR is not LF-normalized")
    lines = text.splitlines()

    manifest: dict[str, tuple[int, str]] = {}
    for line in lines:
        match = MANIFEST.match(line)
        if match:
            name, size, digest = match.groups()
            if name in manifest:
                raise RuntimeError(f"duplicate manifest member: {name}")
            manifest[name] = (int(size), digest)
    if not manifest:
        raise RuntimeError("empty embedded-member manifest")

    extracted: dict[str, bytes] = {}
    index = 0
    while index < len(lines):
        match = HEADING.match(lines[index])
        if not match or match.group(1) not in manifest:
            index += 1
            continue
        name = match.group(1)
        if name in extracted:
            raise RuntimeError(f"duplicate embedded member: {name}")
        if index + 2 >= len(lines) or lines[index + 1] != "" or not lines[
                index + 2].startswith("````"):
            raise RuntimeError(f"malformed opening fence: {name}")
        cursor = index + 3
        content: list[str] = []
        while cursor < len(lines) and lines[cursor] != "````":
            content.append(lines[cursor])
            cursor += 1
        if cursor >= len(lines):
            raise RuntimeError(f"unterminated embedded member: {name}")
        data = ("\n".join(content) + "\n").encode("utf-8")
        size, digest = manifest[name]
        if len(data) != size:
            raise RuntimeError(f"byte mismatch for {name}: {len(data)} != {size}")
        if sha(data) != digest:
            raise RuntimeError(f"hash mismatch for {name}")
        extracted[name] = data
        index = cursor + 1

    if set(extracted) != set(manifest):
        missing = sorted(set(manifest) - set(extracted))
        extra = sorted(set(extracted) - set(manifest))
        raise RuntimeError(f"embedded set mismatch missing={missing} extra={extra}")
    print(
        f"PASS cfr_sha256={sha(raw)} cfr_bytes={len(raw)} "
        f"embedded_members={len(extracted)} embedded_bytes={sum(len(x) for x in extracted.values())}")


if __name__ == "__main__":
    main()
