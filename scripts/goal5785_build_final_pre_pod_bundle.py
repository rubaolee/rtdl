#!/usr/bin/env python3
"""Build the deterministic final Goal5785 nine-app pre-POD bundle."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile


ROOT = Path(__file__).resolve().parents[1]
BASE_SOURCE = ROOT / "history/internal_docs/goal5782_portable_source_v5_20260814.tar.gz"
DATA = ROOT / "history/internal_docs/goal5776_real_scale_data_bundle_20260813.tar.gz"
PREREGISTRATION = ROOT / "history/internal_docs/goal5785_final_nine_app_preregistration_20260815.json"
BUDGET = ROOT / "history/internal_docs/goal5785_final_nine_app_runtime_budget_20260815.json"
EXPECTATION = ROOT / "history/internal_docs/goal5785_pre_registered_expected_value_statement_20260815.md"
TARGET_PREPARE = ROOT / "scripts/goal5776_target_prepare.py"
FORMAL_CONTROLLER = ROOT / "scripts/goal5776_real_scale_formal_controller.py"
FORMAL_CONTROLLER_TEST = ROOT / "tests/goal5776_real_scale_formal_controller_test.py"
SOURCE_MANIFEST_MEMBER = "history/internal_docs/goal5776_source_file_manifest.json"
FORMAL_CONTROLLER_MEMBER = "scripts/goal5776_real_scale_formal_controller.py"
FORMAL_CONTROLLER_TEST_MEMBER = "tests/goal5776_real_scale_formal_controller_test.py"
EXPECTED_BASE_SOURCE_SHA256 = "3237354adeb10dc42858956fe98d33f3f6f41f241c9739820b84aba64e45ebec"
EXPECTED_DATA_SHA256 = "f84ed4396dd9e5928bd222f50fca57af2db727a6d994abfc5844a9b1b12981ad"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _archive(payloads: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(fileobj=output, mode="wb", filename="", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as out:
            for name, data in sorted(payloads.items()):
                info = tarfile.TarInfo(name)
                info.size = len(data)
                info.mtime = 0
                info.mode = 0o755 if name.endswith((".py", ".sh")) else 0o644
                info.uid = info.gid = 0
                info.uname = info.gname = ""
                out.addfile(info, io.BytesIO(data))
    return output.getvalue()


def _safe_members(data: bytes) -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
        for member in archive.getmembers():
            pure = PurePosixPath(member.name)
            parts = tuple(part for part in pure.parts if part not in ("", "."))
            name = "/".join(parts)
            if not parts or pure.is_absolute() or ".." in parts or name in result:
                raise RuntimeError(f"unsafe/duplicate source member: {member.name}")
            if member.isdir():
                continue
            if not member.isfile():
                raise RuntimeError(f"unsupported source member: {member.name}")
            if any(part in (".codex", ".git", "__pycache__") for part in parts) \
                    or name.endswith((".pyc", "librtdl_optix.so")) \
                    or "/build/" in f"/{name}/":
                raise RuntimeError(f"private/prebuilt source member: {name}")
            handle = archive.extractfile(member)
            if handle is None:
                raise RuntimeError(f"unreadable source member: {member.name}")
            result[name] = handle.read()
    return result


def _source_with_manifest() -> tuple[bytes, int, str]:
    base = BASE_SOURCE.read_bytes()
    if _sha(base) != EXPECTED_BASE_SOURCE_SHA256:
        raise RuntimeError("Goal5785 exact Goal5782 source base drifted")
    payloads = _safe_members(base)
    payloads.pop(SOURCE_MANIFEST_MEMBER, None)
    # A4 changes only the formal control-plane entrypoint.  It preserves the
    # admitted venv symlink instead of dereferencing it to a package-less
    # system interpreter.  App/compiler/native/timer bytes remain unchanged.
    payloads[FORMAL_CONTROLLER_MEMBER] = FORMAL_CONTROLLER.read_bytes()
    payloads[FORMAL_CONTROLLER_TEST_MEMBER] = FORMAL_CONTROLLER_TEST.read_bytes()
    rows = [{"path": name, "size_bytes": len(blob), "sha256": _sha(blob)}
            for name, blob in sorted(payloads.items())]
    manifest = (json.dumps({
        "schema": "rtdl.goal5776.source_file_manifest.v1",
        "run_goal_id": 5785,
        "source_base_sha256": EXPECTED_BASE_SOURCE_SHA256,
        "file_count": len(rows),
        "files": rows,
    }, indent=2, sort_keys=True) + "\n").encode()
    payloads[SOURCE_MANIFEST_MEMBER] = manifest
    return _archive(payloads), len(rows), _sha(manifest)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--twin", type=Path, required=True)
    parser.add_argument("--source-output", type=Path, required=True)
    parser.add_argument("--source-twin", type=Path, required=True)
    args = parser.parse_args()
    for path in (args.output, args.twin, args.source_output, args.source_twin):
        if path.exists() or path.is_symlink():
            raise FileExistsError(path)
    data = DATA.read_bytes()
    if _sha(data) != EXPECTED_DATA_SHA256:
        raise RuntimeError("Goal5785 real-scale data archive drifted")
    source, source_file_count, source_manifest_sha = _source_with_manifest()
    preregistration = PREREGISTRATION.read_bytes()
    budget = BUDGET.read_bytes()
    expectation = EXPECTATION.read_bytes()
    target_prepare = TARGET_PREPARE.read_bytes()
    budget_payload = json.loads(budget)
    prereg_payload = json.loads(preregistration)
    if prereg_payload.get("goal") != 5785 \
            or prereg_payload.get("cohort", {}).get("formal_worker_count") != 464 \
            or prereg_payload.get("cohort", {}).get("independent_row_count") != 34:
        raise RuntimeError("Goal5785 preregistration is not exact")
    if budget_payload.get("run_goal_id") != 5785 \
            or budget_payload.get("worker_count") != 464:
        raise RuntimeError("Goal5785 runtime budget is not exact")
    transaction = (json.dumps({
        "schema": "rtdl.goal5785.final_nine_app_transaction.v1",
        "run_goal_id": 5785,
        "protocol_origin_goal_id": 5776,
        "source_base_goal_id": 5782,
        "targeted_predecessor_goal_id": 5784,
        "formal_worker_count": 464,
        "independent_row_count": 34,
        "single_final_matrix_only": True,
        "goal5776_replaced_or_relabelled": False,
        "goal5784_replaced_or_relabelled": False,
        "outer_harness_amendment": "A4__preserve_venv_entrypoint_and_pre_worker_partner_probe",
        "execution_source_changed_from_v2": True,
        "application_compiler_native_timer_or_statistics_changed": False,
    }, indent=2, sort_keys=True) + "\n").encode()
    readme = (
        "# Goal5785 final nine-app V2-direct versus V4 matrix\n\n"
        "This is the single final 464-worker / 34-row CGO cohort. It uses the "
        "unchanged Goal5776 fairness/statistics protocol on the exact Goal5782 "
        "portable source that Goal5784 targeted. Raw schemas retain their "
        "protocol-origin Goal5776 names; TRANSACTION.json binds run_goal_id "
        "5785. One create-only target prepare and a second exact owner authority "
        "are required before formal worker zero.\n"
    ).encode()
    payloads = {
        "SOURCE.tar.gz": source,
        "HARNESS/goal5776_target_prepare.py": target_prepare,
        "PREREGISTRATION.json": preregistration,
        "RUNTIME_BUDGET.json": budget,
        "EXPECTED_VALUE_STATEMENT.md": expectation,
        "TRANSACTION.json": transaction,
        "README.md": readme,
    }
    rows = [{"path": name, "size_bytes": len(blob), "sha256": _sha(blob)}
            for name, blob in sorted(payloads.items())]
    manifest = {
        "schema": "rtdl.goal5776.real_scale_pre_pod_manifest.v1",
        "goal": 5785,
        "run_goal_id": 5785,
        "protocol_origin_goal_id": 5776,
        "bundle_version": 9,
        "goal5785_candidate_revision": 6,
        "source_overrides": [
            {
                "path": FORMAL_CONTROLLER_MEMBER,
                "scope": "formal_control_plane_only__preserve_admitted_venv_entrypoint",
                "sha256": _sha(FORMAL_CONTROLLER.read_bytes()),
            },
            {
                "path": FORMAL_CONTROLLER_TEST_MEMBER,
                "scope": "regression_test__reject_venv_symlink_dereference",
                "sha256": _sha(FORMAL_CONTROLLER_TEST.read_bytes()),
            },
        ],
        "source_base_sha256": EXPECTED_BASE_SOURCE_SHA256,
        "source_archive_sha256": _sha(source),
        "source_manifest_sha256": source_manifest_sha,
        "source_file_count": source_file_count,
        "data_archive_sha256": EXPECTED_DATA_SHA256,
        "preregistration_sha256": _sha(preregistration),
        "runtime_budget_sha256": _sha(budget),
        "expected_value_statement_sha256": _sha(expectation),
        "conservative_budget_seconds": float(
            budget_payload["conservative_budget_seconds"]),
        "focused_test_count": 78,
        "paper_app_count": 9,
        "functional_execution_unit_count": 32,
        "formal_execution_unit_count": 15,
        "cold_execution_unit_count": 15,
        "prepared_execution_unit_count": 14,
        "functional_trial_count": 126,
        "formal_worker_count": 464,
        "independent_comparison_row_count": 34,
        "contains_target_native": False,
        "formal_execution_authorized": False,
        "v3_required_or_executed": False,
        "payload_count": len(rows),
        "payload_bytes": sum(row["size_bytes"] for row in rows),
        "payloads": rows,
    }
    payloads["PORTABLE_MANIFEST.json"] = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    bundle = _archive(payloads)
    for path in (args.output, args.twin):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(bundle)
    for path in (args.source_output, args.source_twin):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(source)
    if args.output.read_bytes() != args.twin.read_bytes() \
            or args.source_output.read_bytes() != args.source_twin.read_bytes():
        raise RuntimeError("Goal5785 deterministic twin mismatch")
    print(json.dumps({
        "bundle_sha256": _sha(bundle),
        "source_archive_sha256": _sha(source),
        "source_manifest_sha256": source_manifest_sha,
        "source_file_count": source_file_count,
        "data_archive_sha256": EXPECTED_DATA_SHA256,
        "payload_count": len(rows),
        "payload_bytes": manifest["payload_bytes"],
        "bundle_twin_byte_identical": True,
        "source_twin_byte_identical": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
