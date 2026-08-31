#!/usr/bin/env python3
"""Close the Goal5801 A1 two-phase cache-commit evidence deterministically."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "history" / "internal_docs" / (
    "goal5801_cache_commit_a1_lx1_untimed_evidence_20260824")
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
    hostile = result["relation"]["failed_predecessor_hostile"]
    if result["status"] != "PASS__TWO_FAMILY_PUBLIC_RTDLEXE_LIFECYCLES" \
            or result["registered_timing_count"] != 0 \
            or hostile["failure_code"] != "RX043_ORACLE_MISMATCH" \
            or hostile["same_bytes_recovery_output"] != [[13, 100]] \
            or hostile["same_bytes_recovery_device_status"][
                "prepared_input_reused"] \
            or hostile["same_bytes_recovery_device_status"][
                "native_source_build_count_delta"] != 1 \
            or not hostile["committed_repeat_device_status"][
                "prepared_input_reused"] \
            or hostile["committed_repeat_device_status"][
                "native_source_build_count_delta"] != 0:
        raise RuntimeError("failed-predecessor cache hostile is not closeable")
    if (EVIDENCE / "evidence/nvrtc_lifecycle.log").read_bytes():
        raise RuntimeError("cache-hit lifecycle reached NVRTC")
    source_map = {
        "source/rtdl_optix_v4_callback_poc.cpp": (
            ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp"),
        "source/rtdl_optix_api.cpp": ROOT / "src/native/optix/rtdl_optix_api.cpp",
        "source/v4_rtdlexe.py": ROOT / "src/rtdsl/v4_rtdlexe.py",
        "source/goal5801_lx1_untimed_smoke.py": (
            ROOT / "scripts/goal5801_lx1_untimed_smoke.py"),
    }
    for relative, current in source_map.items():
        if (EVIDENCE / relative).read_bytes() != current.read_bytes():
            raise RuntimeError(f"executed/local source mismatch: {relative}")
    paths = [path.relative_to(EVIDENCE).as_posix()
             for path in EVIDENCE.rglob("*") if path.is_file()]
    if any("TEST_ONLY_private" in path for path in paths):
        raise RuntimeError("test private key leaked into public evidence")
    for path in (EVIDENCE / "trust_public").glob("*.json"):
        text = path.read_text(encoding="utf-8")
        if "private_exponent" in text or "prime_p" in text or "prime_q" in text:
            raise RuntimeError(f"private RSA material leaked: {path}")


def payload_rows() -> list[dict[str, object]]:
    rows = []
    for path in sorted(EVIDENCE.rglob("*")):
        if not path.is_file() or path == MANIFEST:
            continue
        value = path.read_bytes()
        rows.append({
            "path": path.relative_to(EVIDENCE).as_posix(),
            "bytes": len(value),
            "sha256": sha256(value),
        })
    return rows


def archive_bytes(rows: list[dict[str, object]]) -> bytes:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as archive:
        add_bytes(archive, "manifest.json", MANIFEST.read_bytes())
        for row in rows:
            value = (EVIDENCE / str(row["path"])).read_bytes()
            add_bytes(archive, str(row["path"]), value)
    compressed = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed, mode="wb", filename="", mtime=0) as stream:
        stream.write(raw.getvalue())
    return compressed.getvalue()


def main() -> None:
    if MANIFEST.exists() or ARCHIVE.exists() or TWIN.exists():
        raise FileExistsError("A1 evidence output already exists")
    validate()
    rows = payload_rows()
    manifest = {
        "schema": "rtdl.goal5801.cache_commit_a1_evidence_manifest.v1",
        "status": "PASS__FAILED_PREDECESSOR_CANNOT_AUTHORIZE_NATIVE_REUSE",
        "file_count": len(rows),
        "total_payload_bytes": sum(int(row["bytes"]) for row in rows),
        "files": rows,
        "host": "lx1 GTX1070 CC6.1 Pascal",
        "interpretation": "OptiX_semantics_not_RT_core_performance",
        "registered_performance_timing_count": 0,
        "private_signing_key_included": False,
    }
    MANIFEST.write_bytes(
        json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    first = archive_bytes(rows)
    second = archive_bytes(rows)
    if first != second:
        raise RuntimeError("A1 evidence twin mismatch")
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
