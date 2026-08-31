#!/usr/bin/env python3
"""Recount Goal5813 predecessor/successor source equivalence.

The frozen Goal5809 v4 bundle is the authority for the predecessor source
universe.  This utility verifies every manifest-listed ``source/`` member
against both extracted trees and requires exactly one successor difference:
``src/rtdsl/v4_rtdlexe.py``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import tarfile
from typing import Any


EXPECTED_CHANGED_PATH = "src/rtdsl/v4_rtdlexe.py"
EXPECTED_PREDECESSOR_SHA256 = (
    "3a57a3160999ae54560d73e95e4a01a348c007439a0441893a031dcc87f8032e"
)
EXPECTED_SUCCESSOR_SHA256 = (
    "ea32830ec3ba273523adf947e4e85c460af2ca50aaa316eeb90e1caa39bda097"
)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_record(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": _sha(data)}


def _canonical(value: Any) -> bytes:
    return (json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ) + "\n").encode("ascii")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--predecessor-root", type=Path, required=True)
    parser.add_argument("--successor-root", type=Path, required=True)
    args = parser.parse_args()

    bundle = args.bundle.resolve(strict=True)
    predecessor_root = args.predecessor_root.resolve(strict=True)
    successor_root = args.successor_root.resolve(strict=True)

    with tarfile.open(bundle, "r:gz") as archive:
        manifest_member = archive.extractfile("BUNDLE_MANIFEST.json")
        if manifest_member is None:
            raise SystemExit("BUNDLE_MANIFEST.json is absent")
        manifest_bytes = manifest_member.read()
        manifest = json.loads(manifest_bytes)
        entries = [
            row for row in manifest["files"]
            if row["path"].startswith("source/")
        ]

        archive_mismatch: list[dict[str, Any]] = []
        predecessor_mismatch: list[dict[str, Any]] = []
        successor_mismatch: list[dict[str, Any]] = []
        predecessor_missing: list[str] = []
        successor_missing: list[str] = []

        for entry in entries:
            archive_path = entry["path"]
            relative = archive_path.removeprefix("source/")
            expected = {
                "bytes": int(entry["bytes"]),
                "sha256": str(entry["sha256"]),
            }

            member = archive.extractfile(archive_path)
            if member is None:
                archive_mismatch.append({
                    "path": archive_path,
                    "expected": expected,
                    "observed": "MISSING",
                })
            else:
                archive_data = member.read()
                observed_archive = {
                    "bytes": len(archive_data),
                    "sha256": _sha(archive_data),
                }
                if observed_archive != expected:
                    archive_mismatch.append({
                        "path": archive_path,
                        "expected": expected,
                        "observed": observed_archive,
                    })

            predecessor_path = predecessor_root / relative
            if not predecessor_path.is_file():
                predecessor_missing.append(relative)
            else:
                observed_predecessor = _file_record(predecessor_path)
                if observed_predecessor != expected:
                    predecessor_mismatch.append({
                        "path": relative,
                        "expected": expected,
                        "observed": observed_predecessor,
                    })

            successor_path = successor_root / relative
            if not successor_path.is_file():
                successor_missing.append(relative)
            else:
                observed_successor = _file_record(successor_path)
                if observed_successor != expected:
                    successor_mismatch.append({
                        "path": relative,
                        "predecessor": expected,
                        "successor": observed_successor,
                    })

    exact_expected_mismatch = (
        len(successor_mismatch) == 1
        and successor_mismatch[0]["path"] == EXPECTED_CHANGED_PATH
        and successor_mismatch[0]["predecessor"]["sha256"]
        == EXPECTED_PREDECESSOR_SHA256
        and successor_mismatch[0]["successor"]["sha256"]
        == EXPECTED_SUCCESSOR_SHA256
    )
    passed = (
        not archive_mismatch
        and not predecessor_mismatch
        and not predecessor_missing
        and not successor_missing
        and exact_expected_mismatch
    )

    result: dict[str, Any] = {
        "schema": "rtdl.goal5813.source_equivalence_recount.v1",
        "status": (
            "PASS__ONLY_V4_RTDLEXE_DIFFERS"
            if passed else "FAIL__SOURCE_EQUIVALENCE_NOT_ESTABLISHED"
        ),
        "bundle": {
            "path": str(bundle),
            **_file_record(bundle),
        },
        "bundle_manifest": {
            "bytes": len(manifest_bytes),
            "sha256": _sha(manifest_bytes),
            "declared_internal_sha256": manifest.get(
                "bundle_manifest_sha256"),
        },
        "comparison": {
            "predecessor_root": str(predecessor_root),
            "successor_root": str(successor_root),
            "manifest_source_file_count": len(entries),
            "archive_exact_count": len(entries) - len(archive_mismatch),
            "predecessor_exact_count": (
                len(entries)
                - len(predecessor_mismatch)
                - len(predecessor_missing)
            ),
            "successor_exact_to_predecessor_count": (
                len(entries)
                - len(successor_mismatch)
                - len(successor_missing)
            ),
            "archive_mismatch": archive_mismatch,
            "predecessor_mismatch": predecessor_mismatch,
            "predecessor_missing": predecessor_missing,
            "successor_mismatch": successor_mismatch,
            "successor_missing": successor_missing,
        },
        "claim": (
            "Across every source file declared by the frozen Goal5809 v4 "
            "bundle, the executed predecessor tree is byte-exact and the "
            "successor differs only at src/rtdsl/v4_rtdlexe.py."
        ),
        "claim_boundary": (
            "This comparison covers the frozen bundle's declared source "
            "universe. It does not claim equality of unlisted extra files."
        ),
    }
    result["recount_sha256"] = _sha(_canonical(result))
    print(_canonical(result).decode("ascii"), end="")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
