#!/usr/bin/env python3
"""Independent clean local admission audit for the Goal5785 final bundle."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "history/internal_docs/goal5782_portable_source_v5_20260814.tar.gz"
DATA = ROOT / "history/internal_docs/goal5776_real_scale_data_bundle_20260813.tar.gz"
GOAL5776 = ROOT / "history/internal_docs/goal5776_v9_rtx4000ada_real_scale_v2_v4_evidence_20260814.tar.gz"
GOAL5784 = ROOT / "history/internal_docs/goal5784_a4_final_evidence_20260815.tar.gz"
SOURCE_MANIFEST = "history/internal_docs/goal5776_source_file_manifest.json"
FORMAL_CONTROLLER = "scripts/goal5776_real_scale_formal_controller.py"
FORMAL_CONTROLLER_TEST = "tests/goal5776_real_scale_formal_controller_test.py"


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _members(data: bytes) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for member in archive.getmembers():
            pure = PurePosixPath(member.name)
            parts = tuple(part for part in pure.parts if part not in ("", "."))
            name = "/".join(parts)
            if not parts or pure.is_absolute() or ".." in parts or name in result:
                raise RuntimeError(f"unsafe/duplicate member: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported member: {member.name}")
            handle = archive.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable member: {member.name}")
            result[name] = handle.read()
    return result


def _extract_source(data: bytes, root: Path) -> None:
    members = _members(data)
    for name, blob in members.items():
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(blob)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--bundle-twin", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--source-twin", type=Path, required=True)
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    bundle = args.bundle.read_bytes()
    source = args.source.read_bytes()
    if bundle != args.bundle_twin.read_bytes() or source != args.source_twin.read_bytes():
        raise RuntimeError("Goal5785 deterministic twin mismatch")
    outer = _members(bundle)
    manifest = json.loads(outer["PORTABLE_MANIFEST.json"])
    transaction = json.loads(outer["TRANSACTION.json"])
    preregistration = json.loads(outer["PREREGISTRATION.json"])
    budget = json.loads(outer["RUNTIME_BUDGET.json"])
    expected = {row["path"]: row for row in manifest["payloads"]}
    if set(outer) != set(expected) | {"PORTABLE_MANIFEST.json"}:
        raise RuntimeError("Goal5785 bundle membership mismatch")
    for name, row in expected.items():
        blob = outer[name]
        if len(blob) != row["size_bytes"] or _sha(blob) != row["sha256"]:
            raise RuntimeError(f"Goal5785 bundle payload mismatch: {name}")
    if outer["SOURCE.tar.gz"] != source:
        raise RuntimeError("Goal5785 bundle/source identity mismatch")
    if manifest.get("run_goal_id") != 5785 or transaction.get("run_goal_id") != 5785 \
            or preregistration.get("goal") != 5785 or budget.get("run_goal_id") != 5785:
        raise RuntimeError("Goal5785 transaction identity missing")
    if manifest.get("formal_worker_count") != 464 \
            or manifest.get("independent_comparison_row_count") != 34 \
            or manifest.get("formal_execution_authorized") is not False:
        raise RuntimeError("Goal5785 matrix/admission shape mismatch")
    if any(name.endswith("librtdl_optix.so") for name in outer):
        raise RuntimeError("Goal5785 bundle contains a target native")
    base_members = _members(BASE.read_bytes())
    source_members = _members(source)
    manifest_blob = source_members.pop(SOURCE_MANIFEST)
    changed = {
        name for name in set(source_members) | set(base_members)
        if source_members.get(name) != base_members.get(name)
    }
    if changed != {FORMAL_CONTROLLER, FORMAL_CONTROLLER_TEST}:
        raise RuntimeError(
            "Goal5785 source delta exceeds the reviewed formal-controller fix")
    if source_members[FORMAL_CONTROLLER] != (
        ROOT / FORMAL_CONTROLLER).read_bytes():
        raise RuntimeError("Goal5785 formal-controller override drift")
    if source_members[FORMAL_CONTROLLER_TEST] != (
        ROOT / FORMAL_CONTROLLER_TEST).read_bytes():
        raise RuntimeError("Goal5785 formal-controller regression-test drift")
    source_manifest = json.loads(manifest_blob)
    source_rows = {row["path"]: row for row in source_manifest["files"]}
    if set(source_rows) != set(source_members):
        raise RuntimeError("Goal5785 source manifest membership mismatch")
    for name, blob in source_members.items():
        row = source_rows[name]
        if len(blob) != row["size_bytes"] or _sha(blob) != row["sha256"]:
            raise RuntimeError(f"Goal5785 source manifest mismatch: {name}")
    predecessor_hashes = {
        "goal5776_evidence_sha256": _sha_file(GOAL5776),
        "goal5784_evidence_sha256": _sha_file(GOAL5784),
    }
    if predecessor_hashes != {
        "goal5776_evidence_sha256": "e06d49ddfb018bce1b64b4a2d0802c585e282c8d14b434c15abf1b0da2c04d07",
        "goal5784_evidence_sha256": "a1f2ea4df9386b037df481b64a4fd7bd49a4b0aa081e3f892513870161a8fd18",
    }:
        raise RuntimeError("Goal5785 immutable predecessor drift")
    if _sha_file(DATA) != "f84ed4396dd9e5928bd222f50fca57af2db727a6d994abfc5844a9b1b12981ad":
        raise RuntimeError("Goal5785 data archive drift")
    python = args.python.resolve()
    with tempfile.TemporaryDirectory(prefix="goal5785_clean_audit_") as temporary:
        extracted = Path(temporary) / "source"
        extracted.mkdir()
        _extract_source(source, extracted)
        env = dict(os.environ)
        env["PYTHONPATH"] = os.pathsep.join((
            str(extracted / "src"), str(extracted / "scripts"), str(extracted)))
        tests = subprocess.run([
            str(python), "-m", "unittest", "discover", "-s", str(extracted / "tests"),
            "-p", "goal5776*test.py",
        ], cwd=extracted, env=env, text=True, capture_output=True,
           check=False, timeout=300)
        test_output = tests.stdout + tests.stderr
        if tests.returncode or "Ran 78 tests" not in test_output or "OK" not in test_output:
            raise RuntimeError("Goal5785 exact-source focused suite failed")
        probe = subprocess.run([
            str(python), "-c",
            "import json; from goal5776_real_scale_formal_contract import "
            "schedule, statistical_rows; print(json.dumps({"
            "'workers':len(schedule()),'rows':len(statistical_rows()),"
            "'cold':sum(r['lifecycle']=='installed_cold_compile_prepare_execute' for r in statistical_rows()),"
            "'prepared':sum(r['lifecycle']=='prepared_first_execute' for r in statistical_rows())}))",
        ], cwd=extracted, env=env, text=True, capture_output=True,
           check=True, timeout=60)
        shape = json.loads(probe.stdout)
    if shape != {"workers": 464, "rows": 34, "cold": 15, "prepared": 19}:
        raise RuntimeError("Goal5785 exact-source formal shape mismatch")
    result = {
        "schema": "rtdl.goal5785.clean_pre_pod_audit.v1",
        "goal": 5785,
        "status": "PASS__local_work_complete__target_prepare_and_formal_execution_not_authorized",
        "bundle_sha256": _sha(bundle),
        "source_archive_sha256": _sha(source),
        "source_base_sha256": _sha_file(BASE),
        "source_delta_from_goal5782": {
            "changed_existing_file_count": 2,
            "changed_existing_files": [FORMAL_CONTROLLER, FORMAL_CONTROLLER_TEST],
            "added_file_count": 1,
            "added_file": SOURCE_MANIFEST,
            "application_compiler_native_timer_or_statistics_changed": False,
            "formal_control_plane_changed": True,
        },
        "source_manifest_sha256": _sha(manifest_blob),
        "source_file_count_excluding_manifest": len(source_members),
        "data_archive_sha256": _sha_file(DATA),
        "predecessor_hashes": predecessor_hashes,
        "exact_source_focused_tests": {"ran": 78, "passed": 78},
        "formal_shape": shape,
        "bundle_contains_target_native": False,
        "formal_worker_count": 0,
        "registered_timing_count": 0,
        "minimum_recommended_pod_window_hours": budget["recommended_minimum_pod_window_hours"],
        "prepare_requires_exact_owner_authority": True,
        "formal_requires_second_exact_owner_authority": True,
        "goal5776_replaced_or_relabelled": False,
        "goal5784_replaced_or_relabelled": False,
        "pod_authorized": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
