#!/usr/bin/env python3
"""Download and verify the RayJoin public County x Soil sample."""

from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = APP_ROOT / "data" / "public_sample_manifest.json"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with urllib.request.urlopen(url) as src, tmp.open("wb") as dst:
        while True:
            chunk = src.read(1024 * 1024)
            if not chunk:
                break
            dst.write(chunk)
    tmp.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--data-dir", type=Path, default=APP_ROOT / "_data" / "public_sample")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    args.data_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, object]] = []
    for entry in manifest["files"]:
        path = args.data_dir / entry["filename"]
        if args.force or not path.exists():
            print(f"[fetch] download {entry['filename']}")
            _download(entry["url"], path)
        actual_size = path.stat().st_size
        actual_sha = _sha256(path)
        ok = actual_size == entry["bytes"] and actual_sha == entry["sha256"]
        results.append(
            {
                "role": entry["role"],
                "path": str(path),
                "bytes": actual_size,
                "sha256": actual_sha,
                "ok": ok,
            }
        )
        if not ok:
            raise SystemExit(
                f"manifest verification failed for {path}: "
                f"bytes={actual_size} sha256={actual_sha}"
            )

    print(json.dumps({"schema": "rayjoin.public_sample_fetch.v1", "results": results}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
