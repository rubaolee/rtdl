#!/usr/bin/env python3
"""Build the deterministic, self-manifested Goal5752 evidence archive."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _payloads(root: Path) -> list[dict[str, object]]:
    rows = []
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        if path.name == "EVIDENCE_MANIFEST.json":
            continue
        rows.append({
            "path": path.relative_to(root).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": _sha256(path),
        })
    return rows


def _tarinfo(name: str, size: int, *, directory: bool) -> tarfile.TarInfo:
    item = tarfile.TarInfo(name + ("/" if directory and not name.endswith("/") else ""))
    item.type = tarfile.DIRTYPE if directory else tarfile.REGTYPE
    item.size = 0 if directory else size
    item.mode = 0o755 if directory else 0o644
    item.mtime = 0
    item.uid = item.gid = 0
    item.uname = item.gname = ""
    return item


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.evidence.resolve()
    if not root.is_dir() or root.is_symlink():
        raise RuntimeError("evidence root must be a real directory")
    rows = _payloads(root)
    manifest = {
        "schema": "rtdl.goal5752.evidence_manifest.v1",
        "payload_count": len(rows),
        "payload_bytes": sum(int(row["size_bytes"]) for row in rows),
        "payloads": rows,
    }
    manifest_path = root / "EVIDENCE_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")

    top = root.name
    with args.output.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode="w", format=tarfile.PAX_FORMAT) as archive:
                archive.addfile(_tarinfo(top, 0, directory=True))
                directories = sorted({
                    parent
                    for path in root.rglob("*")
                    for parent in path.relative_to(root).parents
                    if str(parent) != "."
                }, key=lambda path: path.as_posix())
                for directory in directories:
                    archive.addfile(_tarinfo(f"{top}/{directory.as_posix()}", 0, directory=True))
                for path in sorted(item for item in root.rglob("*") if item.is_file()):
                    if path.is_symlink():
                        raise RuntimeError(f"symlink payload rejected: {path}")
                    relative = path.relative_to(root).as_posix()
                    data = path.read_bytes()
                    archive.addfile(
                        _tarinfo(f"{top}/{relative}", len(data), directory=False),
                        io.BytesIO(data),
                    )


if __name__ == "__main__":
    main()
