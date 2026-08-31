"""Verify Goal5798's single CFR from that Markdown file alone."""

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
        raise RuntimeError("empty manifest")

    extracted: dict[str, bytes] = {}
    index = 0
    while index < len(lines):
        heading = HEADING.match(lines[index])
        if not heading or heading.group(1) not in manifest:
            index += 1
            continue
        name = heading.group(1)
        if name in extracted:
            raise RuntimeError(f"duplicate embedded member: {name}")
        if index + 2 >= len(lines) or lines[index + 1] != "" or not lines[
                index + 2].startswith("`````"):
            raise RuntimeError(f"malformed opening fence: {name}")
        cursor = index + 3
        content: list[str] = []
        while cursor < len(lines) and lines[cursor] != "`````":
            content.append(lines[cursor])
            cursor += 1
        if cursor >= len(lines):
            raise RuntimeError(f"unterminated member: {name}")
        data = ("\n".join(content) + "\n").encode("utf-8")
        size, expected = manifest[name]
        if len(data) != size or sha(data) != expected:
            raise RuntimeError(f"member mismatch: {name}")
        extracted[name] = data
        index = cursor + 1
    if set(extracted) != set(manifest):
        raise RuntimeError(
            f"member set mismatch: {sorted(set(manifest) - set(extracted))}")
    print(
        f"PASS cfr_sha256={sha(raw)} cfr_bytes={len(raw)} "
        f"members={len(extracted)} member_bytes={sum(map(len, extracted.values()))}")


if __name__ == "__main__":
    main()
