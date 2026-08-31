#!/usr/bin/env python3
"""Build deterministic, self-contained Goal5764 evidence and twin archives."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "history/internal_docs/goal5764_m6_hierarchy_frontier_evidence_20260812.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5764_m6_hierarchy_frontier_evidence_twin_20260812.tar.gz"
PAYLOADS = (
    "src/rtdsl/v4_hierarchy_frontier.py",
    "scripts/goal5764_m6_hierarchy_fixtures.py",
    "scripts/goal5764_home_hierarchy_frontier_validation.py",
    "scripts/goal5764_recount_home_hierarchy_frontier.py",
    "scripts/goal5764_build_evidence.py",
    "scripts/goal5757_verify_core_freeze.py",
    "tests/goal5764_v4_hierarchy_frontier_test.py",
    "examples/current/research_benchmarks/hierarchy_coverage/v4_hierarchy_coverage_app.py",
    "examples/current/research_benchmarks/hierarchy_coverage/README.md",
    "Paper-reproduction-apps/rt-barneshut-paper/author_contract_reference.py",
    "history/internal_docs/goal5757_lane_probe_evidence_20260811/paper_contracts/rt_barneshut__aggregate_hierarchy_frontier_reduce_v1.json",
    "history/internal_docs/goal5764_v4_core_successor_manifest_20260812.json",
    "history/internal_docs/goal5764_development_lineages_20260812.json",
    "history/internal_docs/goal5764_home_hierarchy_frontier_raw_20260812/RESULT.json",
    "history/internal_docs/goal5764_home_hierarchy_frontier_recount_20260812.json",
    "history/internal_docs/goal5764_home_hierarchy_frontier_final_raw_20260812/RESULT.json",
    "history/internal_docs/goal5764_home_hierarchy_frontier_final_recount_20260812.json",
    "history/internal_docs/goal5764_home_execution_source_20260812.tar.gz",
    "history/internal_docs/goal5764_home_librtdl_optix_20260812.so",
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def archive_bytes() -> tuple[bytes, dict[str, object]]:
    payloads = []
    rows = []
    for path_text in PAYLOADS:
        data = (ROOT / path_text).read_bytes()
        name = path_text.replace("\\", "/")
        payloads.append((name, data))
        rows.append({"path": name, "sha256": sha(data), "size_bytes": len(data)})
    manifest = {
        "schema": "rtdl.goal5764.evidence_manifest.v1",
        "goal": 5764,
        "payload_count": len(rows),
        "payload_bytes": sum(row["size_bytes"] for row in rows),
        "payloads": rows,
    }
    payloads.append((
        "GOAL5764_EVIDENCE_MANIFEST.json",
        (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode(),
    ))
    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode="wb", mtime=0, filename="") as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
            for name, data in sorted(payloads):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                tar.addfile(info, io.BytesIO(data))
    return compressed.getvalue(), manifest


def main() -> None:
    data, manifest = archive_bytes()
    for path in (OUTPUT, TWIN):
        if path.exists():
            raise FileExistsError(path)
        path.write_bytes(data)
    if OUTPUT.read_bytes() != TWIN.read_bytes():
        raise AssertionError("deterministic twin mismatch")
    print(json.dumps({
        "archive_sha256": sha(data),
        "twin_sha256": sha(TWIN.read_bytes()),
        "payload_count": manifest["payload_count"],
        "payload_bytes": manifest["payload_bytes"],
        "byte_identical_twin": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
