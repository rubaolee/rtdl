#!/usr/bin/env python3
"""Build or verify the minimal exact source bundle for a Goal5805 POD."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile
import tempfile
from typing import Any

from experiments.goal5805_successor.protocol import validate_freeze


SCHEMA = "rtdl.goal5805.source_bundle_manifest.v1"


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("Goal5805 JSON root differs")
    return value


def _safe(name: str) -> str:
    pure = PurePosixPath(name)
    if pure.is_absolute() or not name or "\\" in name \
            or any(part in {"", ".", ".."} for part in pure.parts):
        raise RuntimeError(f"Goal5805 unsafe bundle path: {name!r}")
    return name


def build(root: Path, freeze_path: Path, bundle: Path, manifest_path: Path) -> None:
    if bundle.exists() or manifest_path.exists():
        raise RuntimeError("Goal5805 bundle output already exists")
    root = root.resolve(strict=True)
    freeze_path = freeze_path.resolve(strict=True)
    freeze = _read(freeze_path)
    validate_freeze(freeze, root, rehash=True)
    rows = [{"path": "freeze.json", "payload": freeze_path.read_bytes()}]
    for record in freeze["source_manifest"]:
        relative = _safe(str(record["path"]))
        rows.append({"path": "source/" + relative,
                     "payload": (root / relative).read_bytes()})
    rows.sort(key=lambda row: row["path"].encode("utf-8"))
    stream = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=stream, mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
            for row in rows:
                payload = row["payload"]
                info = tarfile.TarInfo(row["path"])
                info.size = len(payload); info.mtime = 0
                info.uid = 0; info.gid = 0; info.uname = ""; info.gname = ""
                info.mode = 0o644
                tar.addfile(info, io.BytesIO(payload))
    packet = stream.getvalue()
    bundle.write_bytes(packet)
    manifest = {
        "schema": SCHEMA,
        "status": "PASS__MINIMAL_EXACT_SOURCE_BUNDLE",
        "bundle_bytes": len(packet), "bundle_sha256": _sha(packet),
        "members": [{"path": row["path"], "bytes": len(row["payload"]),
                     "sha256": _sha(row["payload"])} for row in rows],
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
    }
    manifest_path.write_bytes(json.dumps(
        manifest, indent=2, allow_nan=False, sort_keys=True).encode("utf-8") + b"\n")


def verify(bundle: Path, manifest_path: Path, materialize: Path | None) -> None:
    packet = bundle.resolve(strict=True).read_bytes()
    manifest = _read(manifest_path.resolve(strict=True))
    if manifest.get("schema") != SCHEMA \
            or manifest.get("bundle_bytes") != len(packet) \
            or manifest.get("bundle_sha256") != _sha(packet):
        raise RuntimeError("Goal5805 bundle identity differs")
    expected = {row["path"]: row for row in manifest.get("members", [])}
    observed = {}
    with tarfile.open(fileobj=io.BytesIO(packet), mode="r:gz") as tar:
        for member in tar.getmembers():
            name = _safe(member.name)
            if not member.isfile() or name in observed:
                raise RuntimeError("Goal5805 bundle member type differs")
            handle = tar.extractfile(member)
            if handle is None:
                raise RuntimeError("Goal5805 bundle member unreadable")
            payload = handle.read()
            observed[name] = {"path": name, "bytes": len(payload),
                              "sha256": _sha(payload), "payload": payload}
    projection = [{key: row[key] for key in ("path", "bytes", "sha256")}
                  for row in observed.values()]
    projection.sort(key=lambda row: row["path"].encode("utf-8"))
    if projection != manifest["members"] or set(observed) != set(expected):
        raise RuntimeError("Goal5805 bundle member inventory differs")
    if materialize is not None:
        if materialize.exists():
            raise RuntimeError("Goal5805 materialization root already exists")
        materialize.mkdir(parents=True)
        for name, row in observed.items():
            destination = materialize / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(row["payload"])


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    builder = sub.add_parser("build")
    builder.add_argument("--root", type=Path, required=True)
    builder.add_argument("--freeze", type=Path, required=True)
    builder.add_argument("--bundle", type=Path, required=True)
    builder.add_argument("--manifest", type=Path, required=True)
    verifier = sub.add_parser("verify")
    verifier.add_argument("--bundle", type=Path, required=True)
    verifier.add_argument("--manifest", type=Path, required=True)
    verifier.add_argument("--materialize", type=Path)
    args = parser.parse_args()
    if args.command == "build":
        build(args.root, args.freeze, args.bundle, args.manifest)
    else:
        verify(args.bundle, args.manifest, args.materialize)
    print(json.dumps({"status": "PASS", "formal_worker_count": 0,
                      "registered_performance_timing_count": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

