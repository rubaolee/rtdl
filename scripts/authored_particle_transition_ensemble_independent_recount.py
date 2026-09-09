#!/usr/bin/env python3
"""Reconstruct the natural-scale Particle result without controller imports."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import statistics
import subprocess
import tarfile
import tempfile


SCHEMA = "rtdl.v4.authored_particle.transition_ensemble_recount.v2"
TRANSACTION_SCHEMA = "rtdl.v4.authored_particle.transition_ensemble_formal.v3"
QUERY_COUNT = 160_000_000
WARMUPS = 1
SAMPLES = 3
BOOTSTRAP_DRAWS = 10_000
BOOTSTRAP_SEED = 9_202_609
ORDERS = (
    ("rtdl", "pyoptix"),
    ("pyoptix", "rtdl"),
    ("rtdl", "pyoptix"),
    ("pyoptix", "rtdl"),
    ("pyoptix", "rtdl"),
    ("rtdl", "pyoptix"),
    ("pyoptix", "rtdl"),
    ("rtdl", "pyoptix"),
)
SOURCE_PATHS = (
    "scripts/authored_particle_transition_ensemble_formal_compare.py",
    "scripts/authored_particle_transition_ensemble_worker.py",
    "scripts/generate_authored_particle_transition_ensemble.py",
    "scripts/build_authored_particle_pyoptix_ptx.py",
    "scripts/build_v4_optix_native_snapshot.py",
    "experiments/v4_authored_particle/program.py",
    "experiments/v4_authored_particle/pyoptix_device.cu",
    "experiments/v4_paper_apps_pyoptix/inputs.py",
    "experiments/v4_paper_apps_pyoptix/public_runtime.py",
    "experiments/goal5814_particle/public_pyoptix_owner.py",
    "src/rtdsl/v4.py",
    "src/rtdsl/v4_public_builtin_triangle.py",
    "src/rtdsl/v4_callback_cuda_inline_codegen.py",
    "src/rtdsl/v4_triangle_optix_compiler.py",
    "src/rtdsl/v4_triangle_optix_wrapper_codegen.py",
    "src/rtdsl/v4_triangle_prepared_runtime.py",
    "src/rtdsl/v4_typed_physical_schema.py",
    "src/native/rtdl_optix.cpp",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/native/optix/rtdl_optix_cuda_helpers.cu",
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def binding(path: str | Path) -> dict[str, object]:
    value = Path(path).resolve(strict=True)
    return {
        "path": str(value),
        "bytes": value.stat().st_size,
        "sha256": sha256(value),
    }


def read_json(path: str | Path) -> dict[str, object]:
    def reject_nonfinite(value: str) -> None:
        raise ValueError(f"non-finite JSON value is forbidden: {value}")

    value = json.loads(
        Path(path).read_text(encoding="utf-8"), parse_constant=reject_nonfinite)
    if not isinstance(value, dict):
        raise TypeError(f"JSON object required: {path}")
    return value


def write_new(path: str | Path, value: object) -> None:
    payload = (json.dumps(
        value, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()
    with Path(path).open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def bootstrap_interval(values: list[float]) -> list[float]:
    generator = random.Random(BOOTSTRAP_SEED)
    draws = sorted(statistics.median(
        generator.choices(values, k=len(values)))
        for _ in range(BOOTSTRAP_DRAWS))
    return [draws[249], draws[9749]]


def same_float(left: object, right: object) -> bool:
    return isinstance(left, (int, float)) \
        and isinstance(right, (int, float)) \
        and math.isclose(float(left), float(right), rel_tol=0.0, abs_tol=1e-15)


def check_binding(path: Path, row: object) -> None:
    if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
        raise ValueError("exact file binding required")
    observed = binding(path)
    if observed["bytes"] != row["bytes"] \
            or observed["sha256"] != row["sha256"]:
        raise ValueError(f"archived binding differs: {path}")


def git(repo: Path, *arguments: str, binary: bool = False):
    completed = subprocess.run(
        ["git", "-C", str(repo), *arguments], check=True,
        capture_output=True, text=not binary)
    return completed.stdout if binary else completed.stdout.strip()


def verify_source_closure(repo: Path, prereg: dict[str, object]) -> None:
    commit = prereg["source_commit"]
    if git(repo, "rev-parse", f"{commit}^{{tree}}") != prereg["source_tree"]:
        raise ValueError("source commit/tree identity differs")
    root = Path(prereg["source_root"])
    rows = prereg.get("source_files")
    if not isinstance(rows, list) or len(rows) != len(SOURCE_PATHS):
        raise ValueError("source closure cardinality differs")
    for relative, row in zip(SOURCE_PATHS, rows, strict=True):
        if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"} \
                or Path(row["path"]) != root / relative:
            raise ValueError(f"source binding path differs: {relative}")
        payload = git(repo, "show", f"{commit}:{relative}", binary=True)
        if len(payload) != row["bytes"] \
                or sha256_bytes(payload) != row["sha256"]:
            raise ValueError(f"Git source bytes differ: {relative}")


def expected_command(
    prereg: dict[str, object], arm: str, *, samples: int, formal: bool,
) -> list[str]:
    command = [
        prereg["python"],
        str(Path(prereg["source_root"])
            / "scripts/authored_particle_transition_ensemble_worker.py"),
        "--arm", arm,
        "--base-particle-dir", prereg["base_particle_dir"],
        "--ensemble-dir", prereg["ensemble_dir"],
        "--query-count", str(QUERY_COUNT),
        "--warmups", str(WARMUPS),
        "--samples", str(samples),
    ]
    if formal:
        command.append("--formal-worker")
    if arm == "rtdl":
        command.extend([
            "--native", prereg["native_library"]["path"],
            "--optix-include", prereg["optix_include"],
            "--cuda-include", prereg["cuda_include"],
            "--compute-capability", prereg["gpu"]["compute_capability"],
            "--optix-sdk", prereg["optix_sdk"],
        ])
    elif arm == "pyoptix":
        command.extend(["--pyoptix-ptx", prereg["pyoptix_ptx"]["path"]])
    else:
        raise ValueError(f"unknown arm: {arm}")
    return command


def validate_worker_result(
    prereg: dict[str, object], value: object, arm: str, *,
    samples: int, formal: bool,
) -> None:
    if not isinstance(value, dict):
        raise ValueError("worker result must be an object")
    expected_machine = {
        "hostname": prereg["hostname"],
        "python": prereg["python_version"],
        "gpu_name": prereg["gpu"]["name"],
        "gpu_uuid": prereg["gpu"]["uuid"],
        "driver": prereg["gpu"]["driver"],
        "compute_capability": prereg["gpu"]["compute_capability"],
        "cuda_visible_devices": prereg["gpu"]["uuid"],
        "numba_cuda_use_nvidia_binding": prereg[
            "numba_cuda_use_nvidia_binding"],
    }
    timings = value.get("samples_ns", [])
    if value.get("schema") \
            != "rtdl.v4.authored_particle.transition_ensemble_worker.v2" \
            or value.get("status") != "PASS" \
            or value.get("arm") != arm \
            or value.get("source") != {
                "commit": prereg["source_commit"],
                "tree": prereg["source_tree"],
            } \
            or value.get("machine") != expected_machine \
            or value.get("base_manifest_sha256") \
                != prereg["base_manifest"]["sha256"] \
            or value.get("ensemble_manifest_sha256") \
                != prereg["ensemble_manifest"]["sha256"] \
            or value.get("input_sha256") != prereg["input_sha256"] \
            or value.get("independent_oracle_sha256") \
                != prereg["independent_oracle_sha256"] \
            or value.get("query_count") != QUERY_COUNT \
            or value.get("output_shape") != [QUERY_COUNT, 3] \
            or value.get("output_sha256") != prereg["output_sha256"] \
            or value.get("warmup_count") != WARMUPS \
            or value.get("sample_count") != samples \
            or len(timings) != samples \
            or any(type(item) is not int or item <= 0 for item in timings) \
            or value.get("median_ns") != statistics.median(timings) \
            or any(type(value.get(key)) is not int or value[key] < 0
                   for key in ("prepare_ns", "close_ns")) \
            or value.get("claim_boundary") != {
                "diagnostic_only": True,
                "formal_worker_zero_reached": formal,
                "natural_single_transition_ensemble": True,
                "temporal_particle_simulation": False,
            }:
        raise ValueError(f"{arm} worker contract differs")
    metadata = value.get("metadata", {})
    evidence = value.get("last_execution_evidence", {})
    if arm == "rtdl":
        if metadata.get("path_class") \
                != "public_rtdl_provider_native_closest_prepared" \
                or metadata.get("native_library_sha256") \
                    != prereg["native_library"]["sha256"] \
                or metadata.get("prepared_query_batch_device_resident") is not True \
                or metadata.get("oracle_validation") \
                    != "canonical_u32x3_sha256" \
                or evidence.get("output_sha256") != prereg["output_sha256"] \
                or evidence.get("physical_executor_classification") \
                    != "optix_traversal_observed" \
                or evidence.get("role_counters") \
                    != [0, QUERY_COUNT, 0, 0, QUERY_COUNT, 0, QUERY_COUNT]:
            raise ValueError("RTDL traversal evidence differs")
    else:
        prepared = metadata.get("prepared_query_batch_operation_counts", {})
        counts = evidence.get("operation_counts", {})
        if metadata.get("path_class") \
                != "public_pyoptix_native_closest_prepared" \
                or metadata.get("pyoptix_ptx_sha256") \
                    != prereg["pyoptix_ptx"]["sha256"] \
                or metadata.get("prepared_query_batch_device_resident") is not True \
                or prepared.get("query_h2d_copy_call_count") != 7 \
                or prepared.get("query_h2d_bytes") != QUERY_COUNT * 7 * 4 \
                or prepared.get("pinned_host_allocation_call_count") != 0 \
                or counts.get("query_h2d_copy_call_count") != 0 \
                or counts.get("query_h2d_bytes") != 0 \
                or counts.get("optix_launch_call_count") != 1 \
                or counts.get("output_d2h_bytes") != QUERY_COUNT * 3 * 4 \
                or evidence.get("control") \
                    != [QUERY_COUNT, 0xFFFFFFFF, 0, 0]:
            raise ValueError("PyOptiX operation evidence differs")


def validate_record(
    root: Path, prereg: dict[str, object], record: dict[str, object],
    directory: Path, arm: str, *, samples: int, formal: bool,
) -> dict[str, object]:
    del root
    if record.get("arm") != arm \
            or record.get("samples") != samples \
            or record.get("timed_out") is not False \
            or record.get("returncode") != 0:
        raise ValueError("worker process record differs")
    paths = {
        "command": directory / "COMMAND.json",
        "stdout": directory / "STDOUT.bin",
        "stderr": directory / "STDERR.bin",
        "exit": directory / "EXIT.json",
    }
    for name, path in paths.items():
        check_binding(path, record[name])
    command = json.loads(paths["command"].read_text(encoding="utf-8"))
    if command != expected_command(
            prereg, arm, samples=samples, formal=formal):
        raise ValueError("worker command differs")
    exit_record = read_json(paths["exit"])
    if exit_record != {
        "returncode": record["returncode"],
        "timed_out": record["timed_out"],
        "process_wall_ns": record["process_wall_ns"],
    }:
        raise ValueError("worker exit record differs")
    worker = json.loads(paths["stdout"].read_bytes())
    if worker != record.get("worker_result"):
        raise ValueError("raw worker stdout differs from embedded result")
    validate_worker_result(
        prereg, worker, arm, samples=samples, formal=formal)
    return worker


def verify_archived_artifacts(
    root: Path, prereg: dict[str, object], repo: Path,
) -> None:
    artifacts = root / "artifacts"
    base_manifest = root / "data_manifests/BASE_PARTICLE_MANIFEST.json"
    ensemble_manifest = root / "data_manifests/TRANSITION_ENSEMBLE_MANIFEST.json"
    native = artifacts / "librtdl_optix.so"
    native_build_path = artifacts / "NATIVE_BUILD.json"
    native_log = artifacts / "NATIVE_BUILD.log"
    ptx = artifacts / "PYOPTIX_FACE_FIRST.ptx"
    ptx_build_path = artifacts / "PYOPTIX_BUILD.json"
    for path, row in (
        (base_manifest, prereg["base_manifest"]),
        (ensemble_manifest, prereg["ensemble_manifest"]),
        (native, prereg["native_library"]),
        (native_build_path, prereg["native_build"]),
        (ptx, prereg["pyoptix_ptx"]),
        (ptx_build_path, prereg["pyoptix_build"]),
    ):
        check_binding(path, row)
    ensemble = read_json(ensemble_manifest)
    if ensemble.get("schema") \
            != "rtdl.v4.authored_particle.transition_ensemble.v1" \
            or ensemble.get("queries", {}).get("count") != QUERY_COUNT \
            or ensemble.get("queries", {}).get("distinct_origin_count") \
                != QUERY_COUNT \
            or ensemble.get("claim_boundary", {}).get(
                "distinct_strict_interior_queries") is not True:
        raise ValueError("archived transition-ensemble manifest differs")
    native_build = read_json(native_build_path)
    if native_build.get("status") \
            != "PASS__FRESH_NATIVE_BUILT_AND_REQUIRED_SYMBOLS_EXPORTED" \
            or native_build.get("git_commit") != prereg["source_commit"] \
            or native_build.get("git_commit_after_build") \
                != prereg["source_commit"] \
            or native_build.get("git_status_before_build") != [] \
            or native_build.get("git_status_after_build") != [] \
            or native_build.get("dirty_build_authorized") is not False \
            or native_build.get("all_required_symbols_exported") is not True \
            or native_build.get("native_bytes") != native.stat().st_size \
            or native_build.get("native_sha256") != sha256(native) \
            or native_build.get("log_sha256") != sha256(native_log):
        raise ValueError("archived native build evidence differs")
    ptx_build = read_json(ptx_build_path)
    if ptx_build.get("status") \
            != "PASS__AUTHORED_PARTICLE_PUBLIC_PYOPTIX_PTX_BUILT" \
            or ptx_build.get("source_commit") != prereg["source_commit"] \
            or ptx_build.get("source_tree") != prereg["source_tree"] \
            or ptx_build.get("source_clean_after_build") is not True \
            or ptx_build.get("formal_worker_zero_reached") is not False \
            or ptx_build.get("ptx") != prereg["pyoptix_ptx"]:
        raise ValueError("archived PyOptiX PTX build evidence differs")
    verify_source_closure(repo, prereg)


def recount(*, archive: Path, source_repo: Path) -> dict[str, object]:
    archive = archive.resolve(strict=True)
    source_repo = source_repo.resolve(strict=True)
    with tarfile.open(archive, "r:gz") as package:
        members = package.getmembers()
        names = [member.name for member in members]
        if len(names) != len(set(names)) \
                or not names \
                or any(not (name == "RAW_ARCHIVE_STAGING"
                            or name.startswith("RAW_ARCHIVE_STAGING/"))
                       for name in names) \
                or any(member.issym() or member.islnk() for member in members):
            raise ValueError("formal archive member topology differs")
        with tempfile.TemporaryDirectory(prefix="rtdl-particle-recount-") as temp:
            package.extractall(temp, filter="data")
            root = Path(temp) / "RAW_ARCHIVE_STAGING"
            prereg_path = root / "PREREGISTRATION.json"
            result_path = root / "FORMAL_TRANSACTION/RESULT.json"
            calibration_path = root / "C_ONLY_CALIBRATION/CALIBRATION.json"
            prereg = read_json(prereg_path)
            result = read_json(result_path)
            if prereg.get("schema") != f"{TRANSACTION_SCHEMA}.preregistration" \
                    or prereg.get("status") \
                        != "FROZEN_BEFORE_FORMAL_WORKER_ZERO" \
                    or prereg.get("query_count") != QUERY_COUNT \
                    or prereg.get("warmups") != WARMUPS \
                    or prereg.get("samples") != SAMPLES \
                    or tuple(tuple(row) for row in prereg.get("orders", ())) \
                        != ORDERS \
                    or prereg.get("retry_count") != 0 \
                    or prereg.get("discard_count") != 0 \
                    or prereg.get("numba_cuda_use_nvidia_binding") != "1" \
                    or prereg.get("engineering_targets") != {
                        "paired_median_rtdl_over_pyoptix_at_most": 1.20,
                        "every_block_rtdl_over_pyoptix_at_most": 1.35,
                        "targets_are_not_sample_filters": True,
                    } \
                    or prereg.get("claim_boundary") != {
                        "natural_single_transition_ensemble": True,
                        "temporal_particle_simulation": False,
                        "full_trajectory_tracking": False,
                        "public_claim_authorized": False,
                    }:
                raise ValueError("preregistration contract differs")
            check_binding(prereg_path, result["preregistration"])
            check_binding(calibration_path, prereg["c_only_calibration"])
            verify_archived_artifacts(root, prereg, source_repo)

            calibration = read_json(calibration_path)
            if calibration.get("schema") \
                    != f"{TRANSACTION_SCHEMA}.c_only_calibration" \
                    or calibration.get("status") \
                        != "PASS__THREE_FRESH_C_WORKERS_RETAINED" \
                    or calibration.get("purpose") \
                        != "confirm_previously_selected_160m_natural_scale_without_reselection" \
                    or calibration.get("selection_boundary") != {
                        "scale_changed_after_rtdl_observation": False,
                        "subsecond_confirmation_triggers_reselection": False,
                        "all_confirmation_rows_retained": True,
                    } \
                    or len(calibration.get("workers", [])) != 3:
                raise ValueError("C-only calibration contract differs")
            target_probe = validate_record(
                root, prereg,
                calibration.get("rtdl_target_compatibility_probe"),
                root / "C_ONLY_CALIBRATION/rtdl_target_compatibility_probe",
                "rtdl", samples=1, formal=False)
            calibration_medians = []
            for ordinal, record in enumerate(calibration["workers"]):
                worker = validate_record(
                    root, prereg, record,
                    root / f"C_ONLY_CALIBRATION/worker_{ordinal:02d}",
                    "pyoptix", samples=1, formal=False)
                calibration_medians.append(worker["median_ns"])
            if calibration.get("medians_ns") != calibration_medians \
                    or calibration.get("median_ns") \
                        != statistics.median(calibration_medians):
                raise ValueError("C-only calibration statistics differ")

            if result.get("schema") != f"{TRANSACTION_SCHEMA}.result" \
                    or result.get("source_commit") != prereg["source_commit"] \
                    or result.get("source_tree") != prereg["source_tree"] \
                    or result.get("gpu") != prereg["gpu"] \
                    or result.get("query_count") != QUERY_COUNT \
                    or result.get("input_sha256") != prereg["input_sha256"] \
                    or result.get("output_sha256") != prereg["output_sha256"] \
                    or result.get("worker_count") != 16 \
                    or result.get("timed_sample_count") != 48 \
                    or result.get("warmup_count") != 16 \
                    or result.get("retry_count") != 0 \
                    or result.get("discard_count") != 0 \
                    or result.get("claim_boundary") != {
                        "internal_engineering_target_only": True,
                        "lead_independent_recount_completed": False,
                        "paper_claim_authorized": False,
                        "natural_single_transition_ensemble": True,
                        "temporal_particle_simulation": False,
                        "scale_reselected_after_outcome": False,
                    }:
                raise ValueError("controller result identity differs")
            workers = result.get("workers", [])
            if len(workers) != 16:
                raise ValueError("formal worker count differs")
            ledger_path = root / "FORMAL_TRANSACTION/APPEND_ONLY_LEDGER.jsonl"
            ledger = [json.loads(line) for line in
                      ledger_path.read_text(encoding="utf-8").splitlines()]
            if len(ledger) != 16:
                raise ValueError("append-only ledger count differs")
            reconstructed_workers = []
            for ordinal, record in enumerate(workers):
                block = ordinal // 2
                position = ordinal % 2
                arm = ORDERS[block][position]
                if record.get("ordinal") != ordinal \
                        or record.get("block") != block \
                        or record.get("position") != position \
                        or record.get("status") != "PASS_RETAINED":
                    raise ValueError("formal worker schedule differs")
                worker = validate_record(
                    root, prereg, record,
                    root / f"FORMAL_TRANSACTION/workers/{ordinal:02d}_{arm}",
                    arm, samples=SAMPLES, formal=True)
                expected_ledger = {
                    "ordinal": ordinal,
                    "block": block,
                    "position": position,
                    "arm": arm,
                    "status": "PASS_RETAINED",
                    "median_ns": worker["median_ns"],
                    "stdout_sha256": record["stdout"]["sha256"],
                }
                if ledger[ordinal] != expected_ledger:
                    raise ValueError("append-only ledger row differs")
                reconstructed_workers.append((record, worker))

            block_rows = []
            for block, order in enumerate(ORDERS):
                rows = [row for row in reconstructed_workers
                        if row[0]["block"] == block]
                by_arm = {record["arm"]: worker for record, worker in rows}
                ratio = by_arm["rtdl"]["median_ns"] \
                    / by_arm["pyoptix"]["median_ns"]
                block_rows.append({
                    "block": block,
                    "order": list(order),
                    "rtdl_median_ns": by_arm["rtdl"]["median_ns"],
                    "pyoptix_median_ns": by_arm["pyoptix"]["median_ns"],
                    "rtdl_over_pyoptix": ratio,
                    "rtdl_queries_per_second": (
                        QUERY_COUNT * 1e9 / by_arm["rtdl"]["median_ns"]),
                    "pyoptix_queries_per_second": (
                        QUERY_COUNT * 1e9 / by_arm["pyoptix"]["median_ns"]),
                })
            if block_rows != result.get("block_rows"):
                raise ValueError("reconstructed block rows differ")
            ratios = [row["rtdl_over_pyoptix"] for row in block_rows]
            paired_median = statistics.median(ratios)
            worst = max(ratios)
            bootstrap = bootstrap_interval(ratios)
            if not same_float(
                    paired_median,
                    result.get("paired_median_rtdl_over_pyoptix")) \
                    or not same_float(
                        worst, result.get("worst_block_rtdl_over_pyoptix")) \
                    or result.get("block_bootstrap_95_percent") != bootstrap:
                raise ValueError("reconstructed paired statistics differ")
            rtdl_prepare = statistics.median(
                worker["prepare_ns"] for record, worker in reconstructed_workers
                if record["arm"] == "rtdl")
            pyoptix_prepare = statistics.median(
                worker["prepare_ns"] for record, worker in reconstructed_workers
                if record["arm"] == "pyoptix")
            if not same_float(rtdl_prepare, result.get("rtdl_prepare_median_ns")) \
                    or not same_float(
                        pyoptix_prepare,
                        result.get("pyoptix_prepare_median_ns")):
                raise ValueError("reconstructed preparation statistics differ")
            passed = paired_median <= 1.20 and worst <= 1.35
            expected_status = (
                "PASS__INTERNAL_ENGINEERING_TARGETS__LEAD_RECOUNT_PENDING"
                if passed else
                "FAILED_ENGINEERING_TARGETS__ADVERSE_RESULT_RETAINED")
            if result.get("status") != expected_status:
                raise ValueError("controller gate status differs")
            return {
                "schema": SCHEMA,
                "status": (
                    "PASS__SEPARATE_SCRIPT_RAW_RECONSTRUCTION__"
                    "LEAD_RECOUNT_PENDING"),
                "archive": binding(archive),
                "controller_result_sha256": sha256(result_path),
                "preregistration_sha256": sha256(prereg_path),
                "append_only_ledger_sha256": sha256(ledger_path),
                "source_commit": prereg["source_commit"],
                "source_tree": prereg["source_tree"],
                "source_file_count_verified_from_git": len(SOURCE_PATHS),
                "gpu": prereg["gpu"],
                "query_count": QUERY_COUNT,
                "input_sha256": prereg["input_sha256"],
                "independent_oracle_sha256": prereg[
                    "independent_oracle_sha256"],
                "output_sha256": prereg["output_sha256"],
                "calibration_worker_count": 3,
                "rtdl_target_compatibility_probe_median_ns": target_probe[
                    "median_ns"],
                "calibration_medians_ns": calibration_medians,
                "formal_worker_count": 16,
                "timed_sample_count": 48,
                "warmup_count": 16,
                "block_rows": block_rows,
                "paired_median_rtdl_over_pyoptix": paired_median,
                "worst_block_rtdl_over_pyoptix": worst,
                "block_bootstrap_95_percent": bootstrap,
                "rtdl_prepare_median_ns": rtdl_prepare,
                "pyoptix_prepare_median_ns": pyoptix_prepare,
                "retry_count": 0,
                "discard_count": 0,
                "engineering_targets_passed": passed,
                "claim_boundary": {
                    "natural_single_transition_ensemble": True,
                    "temporal_particle_simulation": False,
                    "full_trajectory_tracking": False,
                    "lead_independent_recount_completed": False,
                    "paper_claim_authorized": False,
                },
            }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--source-repo", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    write_new(args.output, recount(
        archive=args.archive, source_repo=args.source_repo))
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
