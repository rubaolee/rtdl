#!/usr/bin/env python3
"""Build a deterministic, source-only Goal5834 execution projection."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path
import tarfile


ROOT = Path(__file__).resolve().parents[1]
MEMBERS = (
    "src/rtdsl/v4_sphere_optix_wrapper_codegen.py",
    "src/rtdsl/v4_sphere_optix_compiler.py",
    "src/rtdsl/v4_curve_physical_schema.py",
    "src/rtdsl/v4_curve_callback_abi.py",
    "src/rtdsl/v4_curve_optix_wrapper_codegen.py",
    "src/rtdsl/v4_curve_callback_numba_codegen.py",
    "src/rtdsl/v4_builtin_curve_standard_library.py",
    "src/rtdsl/v4_curve_optix_compiler.py",
    "src/rtdsl/v4_curve_prepared_runtime.py",
    "src/rtdsl/v4_public_builtin_curve.py",
    "src/rtdsl/v4_curve.py",
    "examples/first_contact_curve/first_contact_oracle.py",
    "src/native/optix/rtdl_optix_core.cpp",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/native/optix/rtdl_optix_api.cpp",
    "tests/goal5834_builtin_curve_public_path_test.py",
    "tests/goal5834_curve_abi_physical_leaf_audit_test.py",
    "scripts/goal5834_home_builtin_curve_validation.py",
    "scripts/goal5834_verify_home_builtin_curve.py",
    "scripts/goal5834_numeric_counterexample_validation.py",
)


def _sha(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def _archive(rows: list[tuple[str, bytes]]) -> bytes:
    raw = io.BytesIO()
    with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tf:
            for name, body in rows:
                info = tarfile.TarInfo(name)
                info.size = len(body)
                info.mode = 0o444
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                info.mtime = 0
                tf.addfile(info, io.BytesIO(body))
    return raw.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    rows: list[tuple[str, bytes]] = []
    manifest_rows = []
    for name in MEMBERS:
        path = (ROOT / name).resolve(strict=True)
        if not path.is_file() or ROOT not in path.parents:
            raise RuntimeError(f"unsafe source projection member: {name}")
        body = path.read_bytes()
        rows.append((name, body))
        manifest_rows.append({
            "path": name, "size": len(body), "sha256": _sha(body),
        })
    body = _archive(rows)
    twin = _archive(rows)
    if body != twin:
        raise RuntimeError("source projection twin differs")
    archive_path = output / "EXECUTED_SOURCE_PROJECTION_V8.tar.gz"
    twin_path = output / "EXECUTED_SOURCE_PROJECTION_V8_TWIN.tar.gz"
    archive_path.write_bytes(body)
    twin_path.write_bytes(twin)
    manifest = {
        "schema": "rtdl.goal5834.executed_source_projection.v8",
        "archive_sha256": _sha(body),
        "archive_bytes": len(body),
        "member_count": len(manifest_rows),
        "members": manifest_rows,
        "all_members_regular_read_only": True,
        "uid_gid_mtime_zero": True,
        "twin_byte_identical": True,
    }
    manifest_path = output / "EXECUTED_SOURCE_PROJECTION_V8_MANIFEST.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n")
    print(json.dumps({
        "archive_sha256": manifest["archive_sha256"],
        "archive_bytes": manifest["archive_bytes"],
        "member_count": manifest["member_count"],
        "manifest_sha256": _sha(manifest_path.read_bytes()),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
