#!/usr/bin/env python3
"""Create the exact, create-only SQL successor execution freeze.

Run this only after the repaired-v14 wheel has been built and installed into a
fresh isolated site.  It performs identity checks only; it imports no RTDL
module and makes no GPU call.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

import _sqlite3  # type: ignore[import-not-found]

from .build_successor_wheel import (
    EXPECTED_REPAIRED_CORE_SHA256,
    EXPECTED_RTDSL_INIT_SHA256,
    canonical_bytes,
    sha_bytes,
    sha_file,
    source_build_input_projection,
    verify_wheel_against_source,
    wheel_rtdsl_projection,
)
from .run_untimed import (
    EXPECTED_ARTIFACT_SHA256,
    EXPECTED_AUTHORITY_SHA256,
    EXPECTED_BED_REGRESSION_SHA256,
    EXPECTED_CAPACITY,
    EXPECTED_DEPLOYMENT_ID,
    EXPECTED_DRIVER_LIBRARIES,
    EXPECTED_EXECUTABLE_IDENTITY_SHA256,
    EXPECTED_MANIFEST_SHA256,
    EXPECTED_NATIVE_SHA256,
    EXPECTED_TRUST_SHA256,
    EXPECTED_DYNAMIC_STATUS,
    EXPECTED_FAMILY,
    EXPECTED_INDEPENDENT_PROJECTION_SHA256,
    EXPECTED_NATIVE_ABI,
    EXPECTED_RTDSL_MEMBER_COUNT,
    EXPECTED_WHEEL_SHA256,
    _verify_independent_evidence_manifest,
    _verify_independent_install_receipt,
    _verify_independent_projection,
    _verify_independent_wheel_receipt,
    _complete_wheel_projection,
    _installed_site_regular_projection,
    _require_isolated_interpreter_flags,
)


PROJECT_FILE_PATHS = (
    "experiments/goal5803_sql_integer_bag_equijoin/preaction.json",
    "experiments/goal5803_sql_integer_bag_equijoin/task_semantics_freeze.json",
    "experiments/goal5803_sql_integer_bag_equijoin/success_gate_interpretation.json",
    "experiments/goal5803_sql_integer_bag_equijoin/integer_bag_equijoin.py",
    "experiments/goal5803_sql_integer_bag_equijoin/sqlite_oracle.py",
    "experiments/goal5803_sql_integer_bag_equijoin/build_successor_wheel.py",
    "experiments/goal5803_sql_integer_bag_equijoin/run_untimed.py",
    "experiments/goal5803_sql_integer_bag_equijoin/freeze_execution.py",
    "tests/goal5803_sql_integer_bag_equijoin_test.py",
    "tests/goal5803_sql_exact_runner_test.py",
    "tests/goal5803_runtime_overflow_hostile_test.py",
    "history/internal_docs/goal5803_bed_post_core_change_regression_20260827/"
    "goal5803_runtime_overflow_hostile_v14_successor_test.py",
    "history/internal_docs/goal5803_bed_post_core_change_regression_20260827/"
    "v4_rtdlexe.py.post_core_change_v2",
    "history/internal_docs/goal5803_bed_post_core_change_regression_20260827/"
    "v4_rtdlexe_old_to_new.patch",
    "history/internal_docs/goal5803_bed_post_core_change_regression_20260827/"
    "goal5803_post_core_change_regression_result.json",
)

EXPECTED_SOURCE_CORE_FILES = (
    ("src/rtdsl/v4_rtdlexe.py", 217818, EXPECTED_REPAIRED_CORE_SHA256),
    ("src/rtdsl/__init__.py", 317520, EXPECTED_RTDSL_INIT_SHA256),
    ("src/native/optix/rtdl_optix_core.cpp", 384604,
     "1b0c222eafd02ce410e88223baf5155e93c974d7e9426ff9c4a8ef7073eecb70"),
    ("src/native/rtdl_optix_v4_product.cpp", 604,
     "049dfd36478fe2f66439a0f6f0d7f85edbb47bc0d30f97dbd4b4eef735e2d151"),
    ("src/native/optix/rtdl_optix_api.cpp", 523479,
     "f4ec955a1ca4cbf7f9ea961ceab05c91bbd19dcc96ab0ffa3c1b0c12ee060e77"),
    ("Makefile", 11095,
     "659233ad9d9712d838e9c81b88b5401a3f2ece7ea2143a945a5ddf55a33aaceb"),
)


def _fail(message: str) -> None:
    raise RuntimeError(message)


def _row(path: Path, *, display: str | None = None) -> dict[str, object]:
    resolved = path.resolve()
    if not resolved.is_file() or resolved.is_symlink():
        _fail(f"freeze input must be a regular file: {resolved}")
    return {
        "path": display if display is not None else str(resolved),
        "bytes": resolved.stat().st_size,
        "sha256": sha_file(resolved),
    }


def _require(path: Path, *, expected_sha: str, expected_path: str | None = None,
             expected_bytes: int | None = None) -> dict[str, object]:
    row = _row(path)
    if row["sha256"] != expected_sha \
            or (expected_path is not None and row["path"] != expected_path) \
            or (expected_bytes is not None and row["bytes"] != expected_bytes):
        _fail(f"freeze input identity mismatch: {row!r}")
    return row


def _project_files(project_root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for relative in PROJECT_FILE_PATHS:
        path = project_root / relative
        rows.append(_row(path, display=relative))
    bed = next(row for row in rows if row["path"].endswith(
        "goal5803_post_core_change_regression_result.json"))
    archived_core = next(row for row in rows if row["path"].endswith(
        "v4_rtdlexe.py.post_core_change_v2"))
    if bed["sha256"] != EXPECTED_BED_REGRESSION_SHA256 \
            or archived_core["sha256"] != EXPECTED_REPAIRED_CORE_SHA256:
        _fail("preserved repaired-core or BED regression evidence drift")
    return rows


def _source_core(source_root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for relative, size, digest in EXPECTED_SOURCE_CORE_FILES:
        row = _row(source_root / relative, display=relative)
        if row["bytes"] != size or row["sha256"] != digest:
            _fail(f"exact repaired-v14 source drift: {row!r}")
        rows.append(row)
    return rows


def _installed_projection(
    installed_site: Path, wheel_rows: tuple[dict[str, object], ...],
) -> dict[str, object]:
    site = installed_site.resolve()
    observed = []
    for expected in wheel_rows:
        row = _row(site / str(expected["path"]), display=str(expected["path"]))
        if row != expected:
            _fail(f"isolated wheel install differs from wheel: {row!r}")
        observed.append(row)
    extras = []
    expected_paths = {str(row["path"]) for row in wheel_rows}
    for path in (site / "rtdsl").rglob("*"):
        if not path.is_file() or path.is_symlink() \
                or path.suffix == ".pyc" or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(site).as_posix()
        if path.suffix == ".py" or (
                relative.startswith("rtdsl/schemas/") and path.suffix == ".json"):
            if relative not in expected_paths:
                extras.append(relative)
    if extras:
        _fail(f"isolated site has extra rtdsl members: {sorted(extras)!r}")
    whole_rows = _installed_site_regular_projection(site)
    return {
        "path": str(site),
        "rtdsl_member_count": len(observed),
        "rtdsl_projection_sha256": sha_bytes(canonical_bytes(observed)),
        "extra_rtdsl_member_count": 0,
        "installed_before_freeze": True,
        "rtdsl_imported_by_freezer": False,
        "whole_regular_file_count": len(whole_rows),
        "whole_regular_file_projection_sha256": sha_bytes(
            canonical_bytes(list(whole_rows))),
        "root_sitecustomize_or_usercustomize_present": False,
        "rtdsl_pyc_present": False,
    }


def create_execution_freeze(
    *, project_root: Path, source_root: Path, wheel: Path,
    wheel_receipt: Path, wheel_evidence_manifest: Path,
    independent_install_receipt: Path, installed_site: Path, manifest_path: Path,
    native_path: Path, trust_root_path: Path, trust_head_path: Path,
    trust_package_path: Path, driver_root: Path, attempt_journal_path: Path,
    result_output_path: Path, output: Path,
) -> dict[str, object]:
    project_root = project_root.resolve()
    source_root = source_root.resolve()
    output = output.resolve()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    attempt_journal_path = attempt_journal_path.resolve()
    result_output_path = result_output_path.resolve()
    for future_output in (attempt_journal_path, result_output_path):
        if future_output.exists() or future_output.is_symlink():
            raise FileExistsError(future_output)
    interpreter_flags = _require_isolated_interpreter_flags()
    project_files = _project_files(project_root)
    source_core = _source_core(source_root)
    source_projection_before = source_build_input_projection(source_root)

    verified_wheel = verify_wheel_against_source(source_root, wheel)
    if verified_wheel["wheel"]["sha256"] != EXPECTED_WHEEL_SHA256:
        _fail("wheel is not the exact independent Home successor")
    independent_receipt = _verify_independent_wheel_receipt(
        wheel_receipt, wheel)
    independent_evidence = _verify_independent_evidence_manifest(
        wheel_evidence_manifest, verify_payloads=True)
    independent_install = _verify_independent_install_receipt(
        independent_install_receipt, installed_site=installed_site,
        wheel_path=wheel)
    wheel_rows = wheel_rtdsl_projection(wheel)
    complete_wheel_rows = _complete_wheel_projection(wheel)
    complete_wheel_projection_sha = sha_bytes(
        canonical_bytes(list(complete_wheel_rows)))
    independent_projection = _verify_independent_projection(
        wheel_evidence_manifest.resolve().parent /
        "rtdsl_projection_comparison.json", wheel_rows)
    if independent_projection["projection_sha256"] != (
            EXPECTED_INDEPENDENT_PROJECTION_SHA256):
        _fail("independent source/wheel comparison identity drift")
    installed = _installed_projection(installed_site, wheel_rows)
    if installed["rtdsl_projection_sha256"] != verified_wheel[
            "rtdsl_projection_sha256"]:
        _fail("isolated installed projection differs from successor wheel")
    if len(wheel_rows) != EXPECTED_RTDSL_MEMBER_COUNT \
            or str(Path(sys.executable).resolve()) != independent_install[
                "recorded_python"]:
        _fail("freezer is not running in the independently installed v3 venv")

    manifest = _require(
        manifest_path, expected_sha=EXPECTED_MANIFEST_SHA256,
        expected_path=str(manifest_path.resolve()))
    manifest_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    candidate = manifest_payload["candidates"]["relation"]
    required_candidate = {
        "deployment_id": EXPECTED_DEPLOYMENT_ID,
        "artifact_sha256": EXPECTED_ARTIFACT_SHA256,
        "authority_sha256": EXPECTED_AUTHORITY_SHA256,
        "executable_identity_sha256": EXPECTED_EXECUTABLE_IDENTITY_SHA256,
    }
    if any(candidate.get(key) != value for key, value in required_candidate.items()) \
            or manifest_payload.get("native_sha256") != EXPECTED_NATIVE_SHA256:
        _fail("candidate manifest is not the executed BED v14 relation")
    artifact = _require(
        Path(candidate["artifact_path"]), expected_sha=EXPECTED_ARTIFACT_SHA256,
        expected_path=str(Path(candidate["artifact_path"]).resolve()))
    authority = _require(
        Path(candidate["authority_path"]), expected_sha=EXPECTED_AUTHORITY_SHA256,
        expected_path=str(Path(candidate["authority_path"]).resolve()))
    native = _require(
        native_path, expected_sha=EXPECTED_NATIVE_SHA256,
        expected_path=str(native_path.resolve()))
    trust = {}
    for name, path in (
        ("root", trust_root_path), ("head", trust_head_path),
        ("package", trust_package_path),
    ):
        trust[name] = _require(
            path, expected_sha=EXPECTED_TRUST_SHA256[name],
            expected_path=str(path.resolve()))

    driver_root = driver_root.resolve()
    driver_rows = []
    for name, size, digest in EXPECTED_DRIVER_LIBRARIES:
        row = _row(driver_root / name)
        row = {"name": name, "bytes": row["bytes"], "sha256": row["sha256"]}
        if row != {"name": name, "bytes": size, "sha256": digest}:
            _fail(f"driver bridge input drift: {row!r}")
        driver_rows.append(row)

    sqlite_path = Path(_sqlite3.__file__).resolve()
    sqlite_connection = sqlite3.connect(":memory:")
    try:
        sqlite_source_id = sqlite_connection.execute(
            "SELECT sqlite_source_id()").fetchone()[0]
    finally:
        sqlite_connection.close()
    python_path = Path(sys.executable).resolve()
    source_projection_after = source_build_input_projection(source_root)
    if source_projection_after != source_projection_before:
        _fail("repaired-v14 source changed while creating execution freeze")

    bed_row = next(row for row in project_files if row["path"].endswith(
        "goal5803_post_core_change_regression_result.json"))
    payload = {
        "schema": "rtdl.goal5803.sql_integer_bag_equijoin.execution_freeze.v1",
        "date": "2026-08-27",
        "status": "FROZEN_BEFORE_FIRST_SQL_GPU_CALL__NO_SCIENTIFIC_RESULT_YET",
        "creation_rule": {
            "create_only": True,
            "existing_output_refused": True,
            "reseal_or_update_allowed": False,
            "self_hash_embedded": False,
            "reason_self_hash_not_embedded": "a file cannot contain its own SHA-256",
            "successor_must_be_a_new_file": True,
        },
        "chronology": {
            "task_semantics_frozen_before_adapter": True,
            "adapter_oracle_runner_and_tests_frozen_before_first_sql_gpu_call": True,
            "first_sql_gpu_call_count_at_freeze": 0,
            "first_sql_result_count_at_freeze": 0,
            "bed_failure_already_observed": True,
            "sql_successor_selected_after_bed_failure": True,
        },
        "project_files": project_files,
        "source_root": {
            "path": str(source_root),
            "critical_files": source_core,
            "whole_build_input_projection_sha256": sha_bytes(
                canonical_bytes(list(source_projection_before))),
            "whole_build_input_file_count": len(source_projection_before),
            "unchanged_during_freeze": True,
        },
        "successor_wheel": {
            **verified_wheel["wheel"],
            "independent_build_receipt": independent_receipt["identity"],
            "independent_build_receipt_self_sha256": independent_receipt[
                "receipt_self_sha256"],
            "independent_evidence_manifest": independent_evidence["identity"],
            "independent_evidence_manifest_self_sha256": independent_evidence[
                "manifest_self_sha256"],
            "independent_install_receipt": independent_install["identity"],
            "independent_source_wheel_projection": independent_projection,
            "rtdsl_member_count": verified_wheel["rtdsl_member_count"],
            "regular_member_count": len(complete_wheel_rows),
            "complete_wheel_projection_sha256": complete_wheel_projection_sha,
            "installed_projection_sha256": verified_wheel[
                "rtdsl_projection_sha256"],
            "independent_source_wheel_projection_sha256": (
                EXPECTED_INDEPENDENT_PROJECTION_SHA256),
            "repaired_core_sha256": EXPECTED_REPAIRED_CORE_SHA256,
            "packaging_only_successor": True,
            "core_or_native_change": False,
            "double_seed_byte_identical": True,
            "offline_isolated_import": True,
        },
        "isolated_installed_site": installed,
        "execution_environment": {
            "python": _row(python_path),
            "python_version": sys.version,
            "interpreter_flags": interpreter_flags,
            "sqlite_extension": _row(sqlite_path),
            "sqlite_version": sqlite3.sqlite_version,
            "sqlite_source_id": sqlite_source_id,
        },
        "executed_inputs": {
            "manifest": manifest,
            "artifact": artifact,
            "authority": authority,
            "native": native,
            "trust": trust,
        },
        "driver_compatibility_bridge": {
            "root": str(driver_root),
            "libraries": driver_rows,
            "system_packages_may_be_installed_or_changed": False,
            "host_reboot_allowed": False,
        },
        "bed_generic_repair_regression": {
            **bed_row,
            "counts_only_as_generic_repair_regression": True,
            "counts_as_sql_transfer_evidence": False,
            "private_forensic_read_disclosed": True,
        },
        "public_projection_requirements": {
            "top_level_family": EXPECTED_FAMILY,
            "top_level_deployment_id": EXPECTED_DEPLOYMENT_ID,
            "top_level_executable_identity_sha256": (
                EXPECTED_EXECUTABLE_IDENTITY_SHA256),
            "runtime_family": EXPECTED_FAMILY,
            "runtime_native_abi": EXPECTED_NATIVE_ABI,
            "runtime_dynamic_status": EXPECTED_DYNAMIC_STATUS,
            "runtime_triangle_mode": None,
            "minimum_overlap_f32": 1.0,
            "capacity": EXPECTED_CAPACITY,
        },
        "public_behavioral_kats": {
            "threshold": (
                "area exactly 1 accepted; binary32 0x3f7fffff area rejected"),
            "capacity": (
                "projection 4096; K=4096 exact success; fresh K+1 public "
                "RX041 with no result object"),
            "count_as_sql_transfer_evidence": False,
            "private_prepared_state_read_allowed": False,
        },
        "execution": {
            "wheel_execution_mode": True,
            "isolated_installed_site_required": True,
            "source_tree_import_allowed": False,
            "public_lifecycle_only": [
                "install", "load", "LoadedRTDLExecutable.product_projection",
                "prepare", "execute", "close",
            ],
            "private_execution_api_allowed": False,
            "expected_rows_passed_to_execute_allowed": False,
            "handwritten_ptx_sbt_or_pipeline_allowed": False,
            "performance_timing_allowed": False,
            "registered_performance_timing_count": 0,
            "gpu_execution_authorized_by_this_file": False,
            "authorization_boundary": (
                "this file freezes exact bytes; the owner's existing direct "
                "goal-completion command is the execution authority"),
            "output_create_only": True,
            "attempt_journal_required": True,
            "attempt_journal_create_only": True,
            "attempt_journal_path": str(attempt_journal_path),
            "result_output_path": str(result_output_path),
            "silent_retry_with_new_journal_or_output_allowed": False,
            "sql_public_observations_per_case": 2,
            "sql_public_evidence_split": (
                "fast result proves operation-receipt status-before-output; "
                "diagnostic result proves behavioral OptiX; outputs and exact "
                "executable identity must match"),
        },
        "claim_ceiling": {
            "if_pass": (
                "one post-failure project-selected constructive SQLite INTEGER "
                "bag-equijoin application-level reuse witness"),
            "blind_unseen_held_out_or_unbiased_exam": False,
            "broad_generalization_or_transfer_rate": False,
            "new_geometry_or_protocol_family": False,
            "unit_box_geometry_new": False,
            "third_party_user_or_author": False,
            "usability_productivity_or_performance": False,
        },
        "freeze_builder": {
            "path": (
                "experiments/goal5803_sql_integer_bag_equijoin/"
                "freeze_execution.py"),
            "create_only_enforced_by_open_xb": True,
            "imports_rtdsl": False,
            "gpu_call_count": 0,
            "network_call_count": 0,
            "clock_read_or_timing_performed": False,
        },
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as stream:
        stream.write(
            json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
            + b"\n")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--wheel-receipt", type=Path, required=True)
    parser.add_argument("--wheel-evidence-manifest", type=Path, required=True)
    parser.add_argument("--independent-install-receipt", type=Path, required=True)
    parser.add_argument("--installed-site", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--trust-root", type=Path, required=True)
    parser.add_argument("--trust-head", type=Path, required=True)
    parser.add_argument("--trust-package", type=Path, required=True)
    parser.add_argument("--driver-compat-root", type=Path, required=True)
    parser.add_argument("--attempt-journal-path", type=Path, required=True)
    parser.add_argument("--result-output-path", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = create_execution_freeze(
        project_root=args.project_root,
        source_root=args.source_root,
        wheel=args.wheel,
        wheel_receipt=args.wheel_receipt,
        wheel_evidence_manifest=args.wheel_evidence_manifest,
        independent_install_receipt=args.independent_install_receipt,
        installed_site=args.installed_site,
        manifest_path=args.manifest,
        native_path=args.native,
        trust_root_path=args.trust_root,
        trust_head_path=args.trust_head,
        trust_package_path=args.trust_package,
        driver_root=args.driver_compat_root,
        attempt_journal_path=args.attempt_journal_path,
        result_output_path=args.result_output_path,
        output=args.output,
    )
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["PROJECT_FILE_PATHS", "create_execution_freeze"]
