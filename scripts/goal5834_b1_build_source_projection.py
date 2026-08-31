#!/usr/bin/env python3
"""Build deterministic source-only Goal5834-B1 Home projection."""

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
    "examples/curve_boolean_contact/__init__.py",
    "examples/curve_boolean_contact/independent_oracle.py",
    "examples/curve_boolean_contact/fixtures.py",
    "src/native/optix/rtdl_optix_core.cpp",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/native/optix/rtdl_optix_api.cpp",
    "tests/goal5834_b1_curve_boolean_specialization_test.py",
    "tests/goal5834_b1_boolean_fixture_oracle_test.py",
    "tests/goal5834_builtin_curve_public_path_test.py",
    "tests/goal5834_curve_abi_physical_leaf_audit_test.py",
    "scripts/goal5834_b1_prepare_home_execution.py",
    "scripts/goal5834_b1_home_boolean_worker.py",
    "scripts/goal5834_b1_evaluate_raw_boolean_receipt.py",
)


def _sha(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def _archive(rows):
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
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    manifest_rows = []
    for name in MEMBERS:
        path = (ROOT / name).resolve(strict=True)
        if ROOT not in path.parents or not path.is_file():
            raise RuntimeError(f"unsafe source projection member: {name}")
        body = path.read_bytes()
        rows.append((name, body))
        manifest_rows.append({
            "path": name, "bytes": len(body), "sha256": _sha(body),
        })
    body = _archive(rows)
    twin = _archive(rows)
    if body != twin:
        raise RuntimeError("source projection twin differs")
    archive = output / "EXECUTED_SOURCE_PROJECTION_B3_V1.tar.gz"
    twin_path = output / "EXECUTED_SOURCE_PROJECTION_B3_V1_TWIN.tar.gz"
    archive.write_bytes(body)
    twin_path.write_bytes(twin)
    manifest = {
        "schema": "rtdl.goal5834_b3.executed_source_projection.v1",
        "archive_sha256": _sha(body),
        "archive_bytes": len(body),
        "member_count": len(manifest_rows),
        "members": manifest_rows,
        "all_members_regular_read_only": True,
        "uid_gid_mtime_zero": True,
        "twin_byte_identical": True,
        "native_source_changed_from_goal5834": False,
    }
    manifest_path = output / "EXECUTED_SOURCE_PROJECTION_B3_V1_MANIFEST.json"
    manifest_body = (json.dumps(
        manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    manifest_path.write_bytes(manifest_body)
    print(json.dumps({
        "archive_sha256": manifest["archive_sha256"],
        "archive_bytes": manifest["archive_bytes"],
        "member_count": manifest["member_count"],
        "manifest_sha256": _sha(manifest_body),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
