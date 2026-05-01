#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
from pathlib import Path
from typing import Any

from scripts.goal1173_staged_source_archive_manifest import ROOT, build_manifest


DATE = "2026-04-30"
GOAL = "Goal1175 staged source archive builder"
DEFAULT_ARCHIVE = ROOT / "docs/reports/goal1175_rtdl_staged_source_2026-04-30.tar.gz"
DEFAULT_JSON = ROOT / "docs/reports/goal1175_staged_source_archive_2026-04-30.json"
DEFAULT_MD = ROOT / "docs/reports/goal1175_staged_source_archive_2026-04-30.md"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tar_filter(info: tarfile.TarInfo) -> tarfile.TarInfo:
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    info.mtime = 0
    return info


def build_archive(archive_path: Path = DEFAULT_ARCHIVE) -> dict[str, Any]:
    manifest = build_manifest()
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive_path, "w:gz") as archive:
        for row in manifest["files"]:
            rel = Path(row["path"])
            archive.add(ROOT / rel, arcname=f"rtdl_staged_source/{rel}", filter=_tar_filter)
    return {
        "goal": GOAL,
        "date": DATE,
        "archive_path": str(archive_path),
        "archive_sha256": _sha256(archive_path),
        "archive_bytes": archive_path.stat().st_size,
        "manifest_file_count": manifest["file_count"],
        "manifest_aggregate_sha256": manifest["aggregate_sha256"],
        "valid": True,
        "boundary": (
            "This archive packages the staged source set for transfer to a pod. "
            "It is not a benchmark artifact and does not authorize public wording."
        ),
    }


def verify_archive(archive_path: Path, expected_sha256: str) -> dict[str, Any]:
    exists = archive_path.exists()
    actual = _sha256(archive_path) if exists else ""
    return {
        "archive_path": str(archive_path),
        "exists": exists,
        "expected_sha256": expected_sha256,
        "actual_sha256": actual,
        "valid": exists and actual == expected_sha256,
    }


def to_markdown(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Goal1175 Staged Source Archive",
            "",
            f"Date: {payload['date']}",
            "",
            f"Valid: `{payload['valid']}`",
            f"Archive: `{payload['archive_path']}`",
            f"Archive SHA256: `{payload['archive_sha256']}`",
            f"Archive bytes: `{payload['archive_bytes']}`",
            f"Manifest file count: `{payload['manifest_file_count']}`",
            f"Manifest aggregate SHA256: `{payload['manifest_aggregate_sha256']}`",
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build or verify a staged RTDL source archive.")
    parser.add_argument("--archive", type=Path, default=DEFAULT_ARCHIVE)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--verify-sha256")
    args = parser.parse_args(argv)
    if args.verify_sha256:
        payload = verify_archive(args.archive, args.verify_sha256)
    else:
        payload = build_archive(args.archive)
        args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "archive": str(args.archive)}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
