#!/usr/bin/env python3
"""Build deterministic, self-contained Goal5759 functional evidence."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "history/internal_docs/goal5757_v4_core_freeze_manifest_20260811.json"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _build(path: Path, payloads: list[tuple[str, bytes]]) -> None:
    manifest = [{"path": name, "size": len(data), "sha256": _sha(data)}
                for name, data in sorted(payloads)]
    manifest_data = _canonical({
        "schema": "rtdl.goal5759.evidence_manifest.v1",
        "payload_count": len(manifest),
        "payload_bytes": sum(row["size"] for row in manifest),
        "payloads": manifest,
    })
    members = sorted(payloads + [("goal5759_evidence/MANIFEST.json", manifest_data)])
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.GNU_FORMAT) as archive:
                for name, data in members:
                    info = tarfile.TarInfo(name)
                    info.size = len(data); info.mtime = 0; info.uid = info.gid = 0
                    info.uname = info.gname = ""; info.mode = 0o644
                    archive.addfile(info, io.BytesIO(data))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--twin", type=Path, required=True)
    parser.add_argument("--owner-review", type=Path, required=True)
    args = parser.parse_args()
    if args.archive.exists() or args.twin.exists():
        raise FileExistsError("Goal5759 evidence archives are create-only")
    baseline = json.loads(BASELINE.read_text())
    relative_paths = {row["path"] for row in baseline["files"]}
    relative_paths.update({
        "src/rtdsl/v4_triangle_reduction.py",
        "src/rtdsl/v4_triangle_reduction_optix_wrapper_codegen.py",
        "src/rtdsl/v4_triangle_reduction_optix_compiler.py",
        "src/rtdsl/v4_triangle_reduction_optix_runtime.py",
        "scripts/goal5757_verify_core_freeze.py",
        "scripts/goal5758_m1_consumer_fixtures.py",
        "scripts/goal5758_m1_independent_oracles.py",
        "scripts/goal5759_home_triangle_reduction_device_validation.py",
        "scripts/goal5759_recount_home_triangle_reduction.py",
        "scripts/goal5759_build_evidence.py",
        "tests/goal5758_v4_triangle_reduction_test.py",
        "tests/goal5759_v4_triangle_reduction_target_test.py",
        "history/internal_docs/goal5757_v4_core_freeze_manifest_20260811.json",
        "history/internal_docs/goal5759_v4_core_successor_manifest_20260812.json",
        "history/internal_docs/goal5759_home_triangle_reduction_final_recount_20260812.json",
        "history/internal_docs/goal5759_m1_home_true_optix_closure_result_20260812.json",
        "history/internal_docs/goal5759_m1_home_true_optix_closure_technical_report_20260812.md",
        "history/internal_docs/self_review_goal5759_m1_home_true_optix_closure_20260812.md",
    })
    payloads = []
    for relative in sorted(relative_paths):
        source = ROOT / relative
        if not source.is_file():
            raise FileNotFoundError(source)
        payloads.append(("goal5759_evidence/CARRIED/" + relative, source.read_bytes()))
    raw_root = ROOT / "history/internal_docs/goal5759_home_triangle_reduction_final_raw_20260812"
    for source in sorted(item for item in raw_root.rglob("*") if item.is_file()):
        payloads.append((
            "goal5759_evidence/RAW/" + source.relative_to(raw_root).as_posix(),
            source.read_bytes(),
        ))
    payloads.append((
        "goal5759_evidence/OWNER_RETURNED_REVIEW/goal5758_review.txt",
        args.owner_review.read_bytes(),
    ))
    _build(args.archive, payloads)
    _build(args.twin, payloads)
    if args.archive.read_bytes() != args.twin.read_bytes():
        raise RuntimeError("Goal5759 evidence twin differs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
