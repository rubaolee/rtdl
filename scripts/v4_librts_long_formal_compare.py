#!/usr/bin/env python3
"""Preregister and run the paired LibRTS long-workload transaction."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import statistics
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "rtdl.v4.librts.long_query_formal.v1"
PREREG_SCHEMA = f"{SCHEMA}.preregistration"
OPERATIONS = ("point_contains", "range_contains")
ENDPOINTS = ("complete", "prepared")
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
    "scripts/v4_librts_long_c_only_calibrate.py",
    "scripts/v4_librts_long_formal_compare.py",
    "scripts/v4_librts_long_independent_recount.py",
    "scripts/v4_librts_long_worker.py",
    "scripts/generate_v4_librts_long_query_grid.py",
    "scripts/build_v4_optix_native_snapshot.py",
    "experiments/v4_librts_long_workload/__init__.py",
    "experiments/v4_librts_long_workload/query_grid.py",
    "experiments/v4_paper_apps_pyoptix/librts_owner.py",
    "experiments/v4_paper_apps_pyoptix/librts_device.cu",
    "experiments/v4_paper_apps_pyoptix/public_runtime.py",
    "Paper-reproduction-apps/librts-paper/v4_whole_app.py",
    "src/rtdsl/__init__.py",
    "src/rtdsl/v4_aabb_relation_count_lowering.py",
    "src/rtdsl/v4_box_relation_callback.py",
    "src/rtdsl/v4_typed_physical_schema.py",
    "src/rtdsl/aabb_index.py",
    "src/rtdsl/optix_runtime.py",
    "src/native/rtdl_optix.cpp",
    "src/native/optix/rtdl_optix_workloads.cpp",
    "src/native/optix/rtdl_optix_api.cpp",
    "src/native/optix/rtdl_optix_prelude.h",
    "src/native/optix/rtdl_optix_cuda_helpers.cu",
)


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def binding(path: str | Path) -> dict[str, Any]:
    value = Path(path).resolve(strict=True)
    return {"path": str(value), "bytes": value.stat().st_size, "sha256": sha256(value)}


def checked_binding(row: Any) -> Path:
    if not isinstance(row, dict) or set(row) != {"path", "bytes", "sha256"}:
        raise ValueError("exact file binding required")
    path = Path(row["path"]).resolve(strict=True)
    if binding(path) != row:
        raise ValueError(f"bound file changed: {path}")
    return path


def read_json(path: str | Path) -> dict[str, Any]:
    def reject(value: str) -> None:
        raise ValueError(f"nonfinite JSON value is forbidden: {value}")

    result = json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=reject)
    if not isinstance(result, dict):
        raise TypeError(f"JSON object required: {path}")
    return result


def write_new(path: str | Path, value: Any) -> None:
    payload = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("xb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def append_journal(path: Path, value: Any) -> None:
    payload = (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    with path.open("ab") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=root, check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def gpu_identity(uuid: str | None = None) -> dict[str, str]:
    command = ["nvidia-smi"]
    if uuid is not None:
        command.extend(("-i", uuid))
    command.extend((
        "--query-gpu=uuid,name,driver_version,compute_cap",
        "--format=csv,noheader,nounits",
    ))
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    rows = [row.strip() for row in completed.stdout.splitlines() if row.strip()]
    if len(rows) != 1:
        raise RuntimeError("LibRTS formal transaction requires exactly one selected GPU")
    fields = [field.strip() for field in rows[0].split(",")]
    if len(fields) != 4 or (uuid is not None and fields[0] != uuid):
        raise RuntimeError("LibRTS formal GPU identity differs")
    return dict(zip(("uuid", "name", "driver", "compute_capability"), fields))


def manifest_closure(path: Path) -> dict[str, Any]:
    manifest = read_json(path)
    if manifest.get("schema") != "rtdl.v4.librts.distinct_cartesian_query_grid.v1":
        raise ValueError("LibRTS formal query manifest schema differs")
    columns = {
        name: binding(path.parent / row["path"])
        for name, row in manifest["columns"].items()
    }
    for name, row in columns.items():
        if row["sha256"] != manifest["columns"][name]["sha256"]:
            raise ValueError(f"LibRTS query manifest column differs: {name}")
    return {"manifest": binding(path), "columns": columns}


def _package_versions(python: Path) -> dict[str, Any]:
    code = (
        "import importlib.metadata,json,platform;"
        "names=('cuda-bindings','cuda-python','cupy-cuda12x','numba','numpy','pyoptix');"
        "print(json.dumps({'python':platform.python_version(),'packages':"
        "{n:(importlib.metadata.version(n) if any(d.metadata.get('Name','').lower()==n "
        "for d in importlib.metadata.distributions()) else None) for n in names}},sort_keys=True))"
    )
    return json.loads(subprocess.run(
        [str(python), "-c", code], check=True, capture_output=True, text=True,
    ).stdout)


def freeze(args) -> dict[str, Any]:
    source = args.source_root.resolve(strict=True)
    if source != ROOT or git(source, "status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError("formal LibRTS preregistration requires this clean source root")
    commit = git(source, "rev-parse", "HEAD")
    tree = git(source, "rev-parse", "HEAD^{tree}")
    point = manifest_closure(args.point_manifest.resolve(strict=True))
    range_ = manifest_closure(args.range_manifest.resolve(strict=True))
    point_value = read_json(point["manifest"]["path"])
    range_value = read_json(range_["manifest"]["path"])
    if point_value["operation"] != OPERATIONS[0] or range_value["operation"] != OPERATIONS[1]:
        raise ValueError("formal LibRTS query operations differ")
    calibration = read_json(args.calibration)
    if calibration.get("schema") != "rtdl.v4.librts.long_query_c_only_calibration.v1" \
            or calibration.get("status") != "PASS__C_ONLY_LIBRTS_LONG_SCALE_SELECTED" \
            or calibration.get("source_commit") != commit \
            or calibration.get("source_tree") != tree \
            or calibration.get("rtdl_worker_count") != 0 \
            or calibration.get("selected_scale_median_rule_verified") is not True \
            or calibration.get("point_manifest_sha256") != point["manifest"]["sha256"] \
            or calibration.get("range_manifest_sha256") != range_["manifest"]["sha256"] \
            or any(float(calibration[operation]["median_seconds"]) < 1.0 for operation in OPERATIONS):
        raise ValueError("formal LibRTS C-only calibration does not authorize both scales")
    native_manifest = read_json(args.native_manifest)
    native = binding(args.native)
    if native_manifest.get("native_sha256") != native["sha256"] \
            or native_manifest.get("status") \
            != "PASS__FRESH_NATIVE_WITH_EMBEDDED_AABB_INDEX_PROGRAM" \
            or native_manifest.get("git_commit") != commit \
            or native_manifest.get("git_commit_after_build") != commit \
            or native_manifest.get("git_status_before_build") != [] \
            or native_manifest.get("git_status_after_build") != []:
        raise ValueError("native build manifest differs from native library")
    pyoptix_manifest = read_json(args.pyoptix_ptx_manifest)
    pyoptix_ptx = binding(args.pyoptix_ptx)
    pyoptix_program = pyoptix_manifest.get("programs", {}).get("librts", {})
    if pyoptix_manifest.get("status") \
            != "PASS__PREBUILT_PTX_READY_FOR_UNTIMED_DRY_RUN" \
            or pyoptix_manifest.get("source_commit") != commit \
            or pyoptix_manifest.get("source_tree") != tree \
            or pyoptix_manifest.get("source_clean_after_build") is not True \
            or pyoptix_program.get("ptx_sha256") != pyoptix_ptx["sha256"]:
        raise ValueError("PyOptiX PTX build manifest differs from source or PTX")
    python = args.python.resolve(strict=True)
    indexed = binding(args.indexed_npz)
    for closure in (point, range_):
        manifest = read_json(closure["manifest"]["path"])
        if manifest.get("indexed_identity", {}).get("indexed_npz_sha256") != indexed["sha256"]:
            raise ValueError("formal LibRTS query/index identity differs")
    result = {
        "schema": PREREG_SCHEMA,
        "status": "FROZEN_BEFORE_FORMAL_WORKER_ZERO",
        "source_root": str(source),
        "source_commit": commit,
        "source_tree": tree,
        "source_files": [binding(source / relative) for relative in SOURCE_PATHS],
        "python": binding(python),
        "runtime": _package_versions(python),
        "gpu": gpu_identity(args.gpu_uuid),
        "indexed_npz": indexed,
        "point_queries": point,
        "range_queries": range_,
        "native_library": native,
        "native_manifest": binding(args.native_manifest),
        "pyoptix_ptx": pyoptix_ptx,
        "pyoptix_ptx_manifest": binding(args.pyoptix_ptx_manifest),
        "c_only_calibration": binding(args.calibration),
        "optix_sdk": args.optix_sdk,
        "operations": list(OPERATIONS),
        "endpoints": list(ENDPOINTS),
        "orders": [list(order) for order in ORDERS],
        "prepared_warmups": 1,
        "prepared_repetitions": 3,
        "complete_warmups": 0,
        "complete_repetitions": 1,
        "worker_timeout_seconds": args.worker_timeout_seconds,
        "retry_count": 0,
        "discard_count": 0,
        "engineering_targets": {
            "paired_median_rtdl_over_pyoptix_at_most": 1.20,
            "every_block_rtdl_over_pyoptix_at_most": 1.35,
            "targets_are_not_sample_filters": True,
        },
        "claim_boundary": {
            "synthetic_distinct_queries_on_real_parks_index": True,
            "public_claim_authorized": False,
            "formal_worker_zero_reached": False,
        },
    }
    write_new(args.output, result)
    return result


def validate_prereg(path: Path) -> dict[str, Any]:
    value = read_json(path)
    root = Path(value.get("source_root", "")).resolve(strict=True)
    if value.get("schema") != PREREG_SCHEMA \
            or value.get("status") != "FROZEN_BEFORE_FORMAL_WORKER_ZERO" \
            or root != ROOT \
            or git(root, "rev-parse", "HEAD") != value.get("source_commit") \
            or git(root, "rev-parse", "HEAD^{tree}") != value.get("source_tree") \
            or git(root, "status", "--porcelain=v1", "--untracked-files=all") \
            or tuple(value.get("operations", ())) != OPERATIONS \
            or tuple(value.get("endpoints", ())) != ENDPOINTS \
            or tuple(tuple(row) for row in value.get("orders", ())) != ORDERS:
        raise ValueError("formal LibRTS preregistration differs")
    for row in value["source_files"]:
        checked_binding(row)
    for name in (
        "python", "indexed_npz", "native_library", "native_manifest",
        "pyoptix_ptx", "pyoptix_ptx_manifest", "c_only_calibration",
    ):
        checked_binding(value[name])
    for operation in OPERATIONS:
        closure = value["point_queries" if operation == OPERATIONS[0] else "range_queries"]
        checked_binding(closure["manifest"])
        for row in closure["columns"].values():
            checked_binding(row)
    if gpu_identity(value["gpu"]["uuid"]) != value["gpu"]:
        raise ValueError("formal LibRTS GPU changed after preregistration")
    return value


def worker_environment(prereg: dict[str, Any]) -> dict[str, str]:
    environment = dict(os.environ)
    root = prereg["source_root"]
    environment.update({
        "CUDA_VISIBLE_DEVICES": prereg["gpu"]["uuid"],
        "PYTHONPATH": os.pathsep.join((str(Path(root) / "src"), root)),
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "CUDA_CACHE_DISABLE": "1",
        "OPTIX_CACHE_ENABLED": "0",
        "OPTIX_CACHE_MAXSIZE": "0",
    })
    return environment


def worker_command(
    prereg: dict[str, Any], operation: str, endpoint: str, arm: str,
    output: Path,
) -> list[str]:
    closure = prereg["point_queries" if operation == OPERATIONS[0] else "range_queries"]
    warmups = prereg[f"{endpoint}_warmups"]
    repetitions = prereg[f"{endpoint}_repetitions"]
    return [
        prereg["python"]["path"],
        str(Path(prereg["source_root"]) / "scripts/v4_librts_long_worker.py"),
        "--source-root", prereg["source_root"],
        "--arm", arm,
        "--endpoint", endpoint,
        "--operation", operation,
        "--indexed-npz", prereg["indexed_npz"]["path"],
        "--query-manifest", closure["manifest"]["path"],
        "--native", prereg["native_library"]["path"],
        "--pyoptix-ptx", prereg["pyoptix_ptx"]["path"],
        "--optix-sdk", prereg["optix_sdk"],
        "--compute-capability", prereg["gpu"]["compute_capability"],
        "--warmups", str(warmups),
        "--repetitions", str(repetitions),
        "--output", str(output),
    ]


def run_one(
    prereg: dict[str, Any], *, operation: str, endpoint: str, block: int,
    arm: str, directory: Path,
) -> dict[str, Any]:
    directory.mkdir(parents=True, exist_ok=False)
    result_path = directory / "WORKER_RESULT.json"
    command = worker_command(prereg, operation, endpoint, arm, result_path)
    write_new(directory / "COMMAND.json", command)
    started = time.perf_counter_ns()
    process = subprocess.Popen(
        command,
        cwd=prereg["source_root"],
        env=worker_environment(prereg),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=prereg["worker_timeout_seconds"])
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
    ended = time.perf_counter_ns()
    (directory / "STDOUT.bin").write_bytes(stdout)
    (directory / "STDERR.bin").write_bytes(stderr)
    exit_record = {
        "returncode": process.returncode,
        "timed_out": timed_out,
        "process_wall_ns": ended - started,
    }
    write_new(directory / "EXIT.json", exit_record)
    worker = None
    worker_parse_error = None
    if result_path.is_file():
        try:
            worker = read_json(result_path)
        except BaseException as error:
            worker_parse_error = f"{type(error).__name__}: {error}"
    record = {
        "operation": operation,
        "endpoint": endpoint,
        "block": block,
        "arm": arm,
        "command": binding(directory / "COMMAND.json"),
        "stdout": binding(directory / "STDOUT.bin"),
        "stderr": binding(directory / "STDERR.bin"),
        "exit": binding(directory / "EXIT.json"),
        "worker_result": binding(result_path) if result_path.is_file() else None,
        "worker_parse_error": worker_parse_error,
        **exit_record,
    }
    failure_reason = None
    if timed_out:
        failure_reason = "worker_timeout"
    elif process.returncode != 0:
        failure_reason = "worker_nonzero_exit"
    elif worker is None:
        failure_reason = (
            "worker_result_invalid_json"
            if worker_parse_error is not None else "worker_result_absent"
        )
    else:
        manifest = read_json(
            prereg["point_queries" if operation == OPERATIONS[0] else "range_queries"]
            ["manifest"]["path"]
        )
        samples = worker.get("samples_ns")
        expected_repetitions = prereg[f"{endpoint}_repetitions"]
        expected_warmups = prereg[f"{endpoint}_warmups"]
        if worker.get("status") != "PASS__LIBRTS_LONG_QUERY_WORKER" \
                or worker.get("arm") != arm \
                or worker.get("operation") != operation \
                or worker.get("endpoint") != endpoint \
                or worker.get("expected_count_u64") != manifest["expected_count_u64"] \
                or worker.get("query_count") != manifest["query_count"] \
                or worker.get("source", {}).get("commit") != prereg["source_commit"] \
                or worker.get("source", {}).get("tree") != prereg["source_tree"] \
                or worker.get("source", {}).get("dirty") is not False \
                or worker.get("all_queries_distinct") is not True \
                or worker.get("warmup_count") != expected_warmups \
                or worker.get("timed_repetition_count") != expected_repetitions \
                or not isinstance(samples, list) or len(samples) != expected_repetitions \
                or any(type(sample) is not int or sample <= 0 for sample in samples) \
                or len(worker.get("outputs", ())) != expected_repetitions \
                or any(int(row.get("count", -1)) != manifest["expected_count_u64"]
                       for row in worker.get("outputs", ())):
            failure_reason = "worker_contract_mismatch"
    record["worker_contract_validated"] = failure_reason is None
    record["failure_reason"] = failure_reason
    if failure_reason is None:
        metric = worker.get("median_ns") if endpoint == "prepared" else worker.get("complete_task_ns")
        if type(metric) is not int or metric <= 0:
            record["worker_contract_validated"] = False
            record["failure_reason"] = "worker_metric_invalid"
            return record
        record["metric_ns"] = metric
        record["worker"] = worker
    return record


def run_formal(args) -> dict[str, Any]:
    prereg = validate_prereg(args.preregistration.resolve(strict=True))
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    write_new(output / "PREREGISTRATION_BINDING.json", binding(args.preregistration))
    journal = output / "JOURNAL.jsonl"
    records = []
    cells = []
    try:
        for operation in OPERATIONS:
            for endpoint in ENDPOINTS:
                for block, order in enumerate(ORDERS):
                    block_records = {}
                    for arm in order:
                        directory = output / "workers" / operation / endpoint / f"block-{block}" / arm
                        record = run_one(
                            prereg, operation=operation, endpoint=endpoint,
                            block=block, arm=arm, directory=directory,
                        )
                        records.append(record)
                        append_journal(journal, {
                            key: record.get(key) for key in (
                                "operation", "endpoint", "block", "arm", "metric_ns",
                                "returncode", "timed_out", "worker_contract_validated",
                                "failure_reason",
                            )
                        })
                        if not record["worker_contract_validated"]:
                            raise RuntimeError({"worker_failed": record})
                        block_records[arm] = record
                    ratio = block_records["rtdl"]["metric_ns"] / block_records["pyoptix"]["metric_ns"]
                    cells.append({
                        "operation": operation,
                        "endpoint": endpoint,
                        "block": block,
                        "order": list(order),
                        "rtdl_ns": block_records["rtdl"]["metric_ns"],
                        "pyoptix_ns": block_records["pyoptix"]["metric_ns"],
                        "rtdl_over_pyoptix": ratio,
                    })
    except BaseException as error:
        failure = {
            "schema": SCHEMA,
            "status": "FAIL__FORMAL_TRANSACTION_RETAINED",
            "error_type": type(error).__name__,
            "error": str(error),
            "completed_worker_count": len(records),
            "completed_cell_count": len(cells),
            "records": records,
            "cells": cells,
        }
        write_new(output / "FAILURE.json", failure)
        raise
    summaries = []
    passed = True
    for operation in OPERATIONS:
        for endpoint in ENDPOINTS:
            selected = [
                row for row in cells
                if row["operation"] == operation and row["endpoint"] == endpoint
            ]
            ratios = [row["rtdl_over_pyoptix"] for row in selected]
            summary = {
                "operation": operation,
                "endpoint": endpoint,
                "paired_ratio_median": statistics.median(ratios),
                "paired_ratio_min": min(ratios),
                "paired_ratio_max": max(ratios),
                "rtdl_time_median_ns": statistics.median(row["rtdl_ns"] for row in selected),
                "pyoptix_time_median_ns": statistics.median(row["pyoptix_ns"] for row in selected),
                "median_gate_passed": statistics.median(ratios) <= 1.20,
                "every_block_gate_passed": max(ratios) <= 1.35,
            }
            passed = passed and summary["median_gate_passed"] and summary["every_block_gate_passed"]
            summaries.append(summary)
    result = {
        "schema": SCHEMA,
        "status": (
            "PASS__INTERNAL_ENGINEERING_TARGETS__INDEPENDENT_RECOUNT_REQUIRED"
            if passed else "FAIL__ENGINEERING_TARGETS__RESULT_RETAINED"
        ),
        "preregistration": binding(args.preregistration),
        "worker_count": len(records),
        "cell_count": len(cells),
        "retry_count": 0,
        "discard_count": 0,
        "cells": cells,
        "summaries": summaries,
        "claim_boundary": {
            "public_claim_authorized": False,
            "independent_recount_complete": False,
            "synthetic_distinct_queries_on_real_parks_index": True,
        },
    }
    write_new(output / "RESULT.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="mode", required=True)
    freeze_parser = subparsers.add_parser("freeze")
    freeze_parser.add_argument("--source-root", type=Path, required=True)
    freeze_parser.add_argument("--python", type=Path, required=True)
    freeze_parser.add_argument("--gpu-uuid", required=True)
    freeze_parser.add_argument("--indexed-npz", type=Path, required=True)
    freeze_parser.add_argument("--point-manifest", type=Path, required=True)
    freeze_parser.add_argument("--range-manifest", type=Path, required=True)
    freeze_parser.add_argument("--native", type=Path, required=True)
    freeze_parser.add_argument("--native-manifest", type=Path, required=True)
    freeze_parser.add_argument("--pyoptix-ptx", type=Path, required=True)
    freeze_parser.add_argument("--pyoptix-ptx-manifest", type=Path, required=True)
    freeze_parser.add_argument("--calibration", type=Path, required=True)
    freeze_parser.add_argument("--optix-sdk", required=True)
    freeze_parser.add_argument("--worker-timeout-seconds", type=int, default=900)
    freeze_parser.add_argument("--output", type=Path, required=True)
    run_parser = subparsers.add_parser("run")
    run_parser.add_argument("--preregistration", type=Path, required=True)
    run_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = freeze(args) if args.mode == "freeze" else run_formal(args)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
