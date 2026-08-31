#!/usr/bin/env python3
"""Freeze the controlling Goal5801 A2 API/cache evidence and twin."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "history" / "internal_docs" / (
    "goal5801_cache_commit_and_public_api_a3_lx1_untimed_evidence_20260824")
MANIFEST = EVIDENCE / "manifest.json"
ARCHIVE = EVIDENCE.with_name(EVIDENCE.name + ".tar.gz")
TWIN = EVIDENCE.with_name(EVIDENCE.name + "_twin.tar.gz")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def add_bytes(archive: tarfile.TarFile, name: str, value: bytes,
              mode: int = 0o644) -> None:
    info = tarfile.TarInfo(name)
    info.size = len(value)
    info.mode = mode
    info.mtime = 0
    info.uid = 0
    info.gid = 0
    info.uname = ""
    info.gname = ""
    archive.addfile(info, io.BytesIO(value))


def validate() -> None:
    result = json.loads((EVIDENCE / "evidence/lifecycle_result.json").read_bytes())
    relation = result["relation"]["failed_predecessor_hostile"]
    triangle = result["triangle"]["oracle_hostile"]
    if result["status"] != "PASS__TWO_FAMILY_PUBLIC_RTDLEXE_LIFECYCLES" \
            or result["registered_timing_count"] != 0 \
            or relation["failure_code"] != "RX043_ORACLE_MISMATCH" \
            or relation["same_bytes_recovery_device_status"][
                "native_source_build_count_delta"] != 1 \
            or relation["same_bytes_recovery_device_status"][
                "prepared_input_reused"] \
            or relation["committed_repeat_device_status"][
                "native_source_build_count_delta"] != 0 \
            or not relation["committed_repeat_device_status"][
                "prepared_input_reused"] \
            or triangle["failure_code"] != "RX043_ORACLE_MISMATCH" \
            or triangle["same_bytes_recovery_output"] != 9 \
            or triangle["same_bytes_recovery_device_status"][
                "prepared_input_reused"]:
        raise RuntimeError("Goal5801 A2 hostile contract mismatch")
    if (EVIDENCE / "evidence/nvrtc_lifecycle.log").read_bytes():
        raise RuntimeError("A2 lifecycle entered NVRTC")
    sources = {
        "source/rtdl_optix_v4_callback_poc.cpp": (
            ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp"),
        "source/rtdl_optix_api.cpp": ROOT / "src/native/optix/rtdl_optix_api.cpp",
        "source/v4_rtdlexe.py": ROOT / "src/rtdsl/v4_rtdlexe.py",
        "source/__init__.py": ROOT / "src/rtdsl/__init__.py",
        "source/goal5801_lx1_untimed_smoke.py": (
            ROOT / "scripts/goal5801_lx1_untimed_smoke.py"),
        "source/goal5801_rtdlexe_trust.py": (
            ROOT / "scripts/goal5801_rtdlexe_trust.py"),
        "source/goal5801_rtdlexe_runtime_test.py": (
            ROOT / "tests/goal5801_rtdlexe_runtime_test.py"),
        "source/v4_rtdlexe_deployment.md": ROOT / "docs/v4_rtdlexe_deployment.md",
    }
    for relative, current in sources.items():
        if (EVIDENCE / relative).read_bytes() != current.read_bytes():
            raise RuntimeError(f"executed/delivered source mismatch: {relative}")
    if any("TEST_ONLY_private" in path.relative_to(EVIDENCE).as_posix()
           for path in EVIDENCE.rglob("*") if path.is_file()):
        raise RuntimeError("test private key leaked")


def rows() -> list[dict[str, object]]:
    return [{
        "path": path.relative_to(EVIDENCE).as_posix(),
        "bytes": len(value := path.read_bytes()),
        "sha256": sha256(value),
    } for path in sorted(EVIDENCE.rglob("*"))
      if path.is_file() and path != MANIFEST]


def archive_bytes(payloads: list[dict[str, object]]) -> bytes:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as archive:
        add_bytes(archive, "manifest.json", MANIFEST.read_bytes())
        for row in payloads:
            add_bytes(archive, str(row["path"]),
                      (EVIDENCE / str(row["path"])).read_bytes())
    out = io.BytesIO()
    with gzip.GzipFile(fileobj=out, mode="wb", filename="", mtime=0) as stream:
        stream.write(raw.getvalue())
    return out.getvalue()


def main() -> None:
    if MANIFEST.exists() or ARCHIVE.exists() or TWIN.exists():
        raise FileExistsError("A2 evidence already exists")
    validate()
    payloads = rows()
    manifest = {
        "schema": "rtdl.goal5801.public_api_a2_evidence_manifest.v2",
        "status": (
            "PASS__CACHE_COMMIT__DISTINCT_INPUT_NAMES__TWO_FAMILY_ORACLES__"
            "EXACT_HARDENED_TEST_TRUST_TOOL"),
        "file_count": len(payloads),
        "total_payload_bytes": sum(int(row["bytes"]) for row in payloads),
        "files": payloads,
        "registered_performance_timing_count": 0,
        "private_signing_key_included": False,
        "host": "lx1 GTX1070 CC6.1 Pascal",
        "interpretation": "OptiX_semantics_not_RT_core_performance",
    }
    MANIFEST.write_bytes(
        json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    first = archive_bytes(payloads)
    second = archive_bytes(payloads)
    if first != second:
        raise RuntimeError("A2 evidence twin mismatch")
    ARCHIVE.write_bytes(first)
    TWIN.write_bytes(second)
    print(json.dumps({
        "manifest_sha256": sha256(MANIFEST.read_bytes()),
        "archive_sha256": sha256(first),
        "archive_bytes": len(first),
        "twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
