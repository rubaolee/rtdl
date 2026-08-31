#!/usr/bin/env python3
"""Independent clean extraction/static readiness audit for Goal5784."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import tempfile


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_extract(archive_path: Path, target: Path) -> list[str]:
    names: list[str] = []
    with tarfile.open(archive_path, "r:gz") as archive:
        for member in archive.getmembers():
            path = PurePosixPath(member.name)
            parts = tuple(part for part in path.parts if part not in ("", "."))
            name = "/".join(parts)
            if not parts or path.is_absolute() or ".." in parts or name in names:
                raise RuntimeError(f"unsafe/duplicate archive member: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported archive member: {member.name}")
            destination = target.joinpath(*parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            handle = archive.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable archive member: {member.name}")
            destination.write_bytes(handle.read())
            names.append(name)
    return names


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--data-bundle", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    with tempfile.TemporaryDirectory(prefix="goal5784-clean-audit-") as td:
        root = Path(td)
        outer_root = root / "outer"
        outer_root.mkdir()
        outer_names = _safe_extract(args.bundle, outer_root)
        manifest = json.loads((outer_root / "PORTABLE_MANIFEST.json").read_text(
            encoding="utf-8"))
        rows = {str(row["path"]): row for row in manifest["payloads"]}
        if set(outer_names) != set(rows) | {"PORTABLE_MANIFEST.json"}:
            raise RuntimeError("Goal5784 outer membership mismatch")
        for name, row in rows.items():
            path = outer_root / name
            if path.stat().st_size != int(row["size_bytes"]) \
                    or _sha(path) != row["sha256"]:
                raise RuntimeError(f"Goal5784 outer payload mismatch: {name}")
        if manifest.get("formal_worker_count") != 128 \
                or manifest.get("independent_comparison_row_count") != 8 \
                or manifest.get("formal_execution_authorized") is not False:
            raise RuntimeError("Goal5784 manifest scope mismatch")
        source_root = root / "source"
        source_root.mkdir()
        source_names = _safe_extract(outer_root / "SOURCE.tar.gz", source_root)
        if any(".codex" in PurePosixPath(name).parts
               or name.endswith((".pyc", "librtdl_optix.so"))
               or "/build/" in f"/{name}/" for name in source_names):
            raise RuntimeError("Goal5784 source contains private/prebuilt state")
        docs = source_root / "history/internal_docs"
        docs.mkdir(parents=True, exist_ok=True)
        (docs / "goal5784_targeted_modern_rtx_preregistration_20260814.json").write_bytes(
            (outer_root / "PREREGISTRATION.json").read_bytes())
        (docs / "goal5784_targeted_formal_runtime_budget_20260814.json").write_bytes(
            (outer_root / "RUNTIME_BUDGET.json").read_bytes())
        (docs / "goal5784_pre_registered_expected_value_statement_20260814.md").write_bytes(
            (outer_root / "EXPECTED_VALUE_STATEMENT.md").read_bytes())
        harness = outer_root / "HARNESS"
        compile_paths = sorted(str(path) for path in harness.glob("*.py"))
        subprocess.run([sys.executable, "-m", "py_compile", *compile_paths],
                       check=True, timeout=60)
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join((
            str(harness), str(source_root / "src"),
            str(source_root / "scripts"), str(source_root)))
        env["RTDL_GOAL5784_PREREGISTRATION_PATH"] = str(
            outer_root / "PREREGISTRATION.json")
        env["RTDL_GOAL5784_RUNTIME_BUDGET_PATH"] = str(
            outer_root / "RUNTIME_BUDGET.json")
        env["RTDL_GOAL5784_EXPECTED_VALUE_STATEMENT_PATH"] = str(
            outer_root / "EXPECTED_VALUE_STATEMENT.md")
        env["RTDL_GOAL5784_HARNESS_ROOT"] = str(harness)
        tests = subprocess.run([
            sys.executable, "-m", "unittest",
            "tests.goal5778_v4_checked_u64_device_reduction_test",
            "tests.goal5782_canonical_packed_hierarchy_binding_test",
            "goal5784_targeted_pre_pod_test",
        ], cwd=source_root, env=env, text=True, capture_output=True,
            timeout=120, check=True)
        data_root = root / "data"
        data_root.mkdir()
        data_names = _safe_extract(args.data_bundle, data_root)
        data_manifest = json.loads((data_root / "DATA_MANIFEST.json").read_text(
            encoding="utf-8"))
        expected_data = {str(row["path"]): row
                         for row in data_manifest["files"]}
        if set(data_names) != set(expected_data) | {"DATA_MANIFEST.json"} \
                or data_manifest.get("file_count") != 5:
            raise RuntimeError("Goal5784 targeted data membership mismatch")
        for name, row in expected_data.items():
            path = data_root / name
            if path.stat().st_size != int(row["size_bytes"]) \
                    or _sha(path) != row["sha256"]:
                raise RuntimeError(f"Goal5784 data payload mismatch: {name}")
        result = {
            "schema": "rtdl.goal5784.clean_pre_pod_audit_result.v1",
            "bundle_sha256": _sha(args.bundle),
            "data_archive_sha256": _sha(args.data_bundle),
            "source_archive_sha256": _sha(outer_root / "SOURCE.tar.gz"),
            "outer_payload_count": len(rows),
            "source_file_count": len(source_names),
            "data_payload_count": len(expected_data),
            "focused_test_count": manifest["focused_test_count"],
            "focused_tests_passed": "OK" in tests.stderr,
            "formal_worker_count": 0,
            "registered_formal_timing_count": 0,
            "pod_used_or_authorized": False,
            "clean_extraction_passed": True,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8", newline="\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
