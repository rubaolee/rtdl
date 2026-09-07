#!/usr/bin/env python3
"""Safely extract and verify the frozen nine-app real-scale data archive."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from goal5776_target_prepare import _extract_data

EXPECTED_ARCHIVE_SHA256 = (
    "f84ed4396dd9e5928bd222f50fca57af2db727a6d994abfc5844a9b1b12981ad"
)
EXPECTED_ARCHIVE_BYTES = 1_155_932_998


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()
    archive = args.archive.resolve(strict=True)
    if archive.stat().st_size != EXPECTED_ARCHIVE_BYTES:
        raise RuntimeError("real-scale data archive byte count differs")
    archive_sha256 = _sha(archive)
    if archive_sha256 != EXPECTED_ARCHIVE_SHA256:
        raise RuntimeError("real-scale data archive SHA-256 differs")
    output = args.output_root.absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    manifest = _extract_data(archive, output)
    manifest_path = output / "DATA_MANIFEST.json"
    receipt = {
        "schema": "rtdl.v4_paper_apps_pyoptix.data_extraction.v1",
        "status": "PASS__ARCHIVE_AND_EVERY_MEMBER_VERIFIED",
        "archive_path": str(archive),
        "archive_bytes": EXPECTED_ARCHIVE_BYTES,
        "archive_sha256": archive_sha256,
        "data_root": str(output / "DATA"),
        "data_manifest_path": str(manifest_path),
        "data_manifest_sha256": _sha(manifest_path),
        "data_member_count": len(manifest["files"]),
        "formal_worker_zero_reached": False,
        "performance_result_exists": False,
    }
    receipt_path = output / "EXTRACTION_RECEIPT.json"
    with receipt_path.open("x", encoding="utf-8") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
