#!/usr/bin/env python3
"""Build deterministic, reviewer-visible Goal5784 final evidence and twin."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "history/internal_docs/goal5784_a4_final_evidence_20260815.tar.gz"
TWIN = ROOT / "history/internal_docs/goal5784_a4_final_evidence_twin_20260815.tar.gz"

FILES = (
    "history/internal_docs/goal5784_targeted_modern_rtx_preregistration_20260814.md",
    "history/internal_docs/goal5784_targeted_modern_rtx_preregistration_20260814.json",
    "history/internal_docs/goal5784_targeted_formal_runtime_budget_20260814.json",
    "history/internal_docs/goal5784_pre_registered_expected_value_statement_20260814.md",
    "history/internal_docs/goal5784_owner_create_only_prepare_authority_v5_20260815.json",
    "history/internal_docs/goal5784_owner_formal_authority_v5_20260815.json",
    "history/internal_docs/goal5784_targeted_pre_pod_bundle_v5_20260815.tar.gz",
    "history/internal_docs/goal5784_clean_pre_pod_audit_result_v5_20260815.json",
    "history/internal_docs/goal5784_a2_v5_prepared_evidence_20260815.tar.gz",
    "history/internal_docs/self_review_goal5784_a2_v5_create_only_prepare_20260815.md",
    "history/internal_docs/goal5784_a3_v4_s1_terminal_evidence_20260815.tar.gz",
    "history/internal_docs/goal5784_a3_v4_s1_worker_0000_20260815.json",
    "history/internal_docs/self_review_goal5784_a3_v4_s1_failure_and_v5_successor_20260815.md",
    "history/internal_docs/goal5784_a3_v5_raw_preservation_20260815.tar.gz",
    "history/internal_docs/goal5784_a4_independent_raw_recount_20260815.py",
    "history/internal_docs/goal5784_a4_independent_raw_recount_20260815.json",
    "history/internal_docs/goal5784_a4_targeted_modern_rtx_result_20260815.json",
    "history/internal_docs/goal5784_a4_targeted_modern_rtx_technical_report_20260815.md",
    "history/internal_docs/self_review_goal5784_a3_v5_formal_execution_20260815.md",
)

EXTERNAL_SIDECARS = (
    "history/internal_docs/goal5784_targeted_data_bundle_v1_20260814.tar.gz",
    "history/internal_docs/goal5784_targeted_data_bundle_v1_twin_20260814.tar.gz",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def deterministic_archive(payloads: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tar:
            for name, data in sorted(payloads.items()):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o755 if name.endswith((".py", ".sh")) else 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                tar.addfile(info, io.BytesIO(data))
    return output.getvalue()


def main() -> None:
    if OUT.exists() or TWIN.exists():
        raise FileExistsError("Goal5784 final evidence output already exists")

    payloads: dict[str, bytes] = {}
    for name in FILES:
        path = ROOT / name
        if not path.is_file():
            raise FileNotFoundError(path)
        if any(part in (".codex", ".git", "__pycache__") for part in Path(name).parts):
            raise RuntimeError(f"private/cache evidence member: {name}")
        payloads[name] = path.read_bytes()

    rows = [
        {"path": name, "sha256": digest(data), "size_bytes": len(data)}
        for name, data in sorted(payloads.items())
    ]
    sidecars = []
    for name in EXTERNAL_SIDECARS:
        path = ROOT / name
        if not path.is_file():
            raise FileNotFoundError(path)
        data = path.read_bytes()
        sidecars.append({
            "path": name,
            "sha256": digest(data),
            "size_bytes": len(data),
            "embedded": False,
        })
    if sidecars[0]["sha256"] != sidecars[1]["sha256"]:
        raise RuntimeError("Goal5784 data archive twin differs")

    manifest = (
        json.dumps(
            {
                "schema": "rtdl.goal5784.a4.final_evidence_manifest.v1",
                "run_goal_id": 5784,
                "payload_count": len(rows),
                "payload_bytes": sum(row["size_bytes"] for row in rows),
                "manifest_is_not_a_payload": True,
                "external_sidecars": sidecars,
                "payloads": rows,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n"
    ).encode()
    final = deterministic_archive(
        {**payloads, "GOAL5784_A4_EVIDENCE_MANIFEST.json": manifest}
    )
    OUT.write_bytes(final)
    TWIN.write_bytes(final)
    if OUT.read_bytes() != TWIN.read_bytes():
        raise RuntimeError("Goal5784 final evidence twin differs")
    print(json.dumps({
        "archive_sha256": digest(final),
        "payload_count": len(rows),
        "payload_bytes": sum(row["size_bytes"] for row in rows),
        "external_data_sidecar_sha256": sidecars[0]["sha256"],
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
