#!/usr/bin/env python3
"""Select LibRTS long-query scales using only fresh public-PyOptiX workers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import statistics
import subprocess
import time
import traceback
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "rtdl.v4.librts.long_query_c_only_calibration.v1"
QUERY_SCHEMA = "rtdl.v4.librts.distinct_cartesian_query_grid.v1"
OPERATIONS = ("point_contains", "range_contains")
FRESH_PROCESSES_PER_SCALE = 3


def sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def binding(path: str | Path) -> dict[str, Any]:
    value = Path(path).resolve(strict=True)
    return {"path": str(value), "bytes": value.stat().st_size, "sha256": sha256(value)}


def read_json(path: str | Path) -> dict[str, Any]:
    def reject(value: str) -> None:
        raise ValueError(f"nonfinite JSON value is forbidden: {value}")

    result = json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=reject)
    if not isinstance(result, dict):
        raise TypeError(f"JSON object required: {path}")
    return result


def write_new(path: str | Path, value: Any) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()
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
        ["git", *arguments], cwd=root, check=True, capture_output=True, text=True,
    ).stdout.strip()


def validate_candidates(paths: list[Path], operation: str) -> list[dict[str, Any]]:
    if not paths:
        raise ValueError(f"at least one {operation} candidate is required")
    result = []
    previous_count = 0
    source_sha = None
    indexed_identity = None
    for path in paths:
        resolved = path.resolve(strict=True)
        manifest = read_json(resolved)
        count = manifest.get("query_count")
        if manifest.get("schema") != QUERY_SCHEMA or manifest.get("operation") != operation \
                or type(count) is not int or count <= previous_count \
                or manifest.get("all_queries_distinct") is not True:
            raise ValueError(f"invalid or unordered {operation} calibration candidate: {path}")
        current_source = manifest.get("source_query_sha256")
        current_index = manifest.get("indexed_identity")
        if source_sha is not None and current_source != source_sha:
            raise ValueError(f"{operation} calibration candidates use different source queries")
        if indexed_identity is not None and current_index != indexed_identity:
            raise ValueError(f"{operation} calibration candidates use different indexed data")
        expected_columns = (
            {"x", "y"}
            if operation == "point_contains"
            else {"min_x", "min_y", "max_x", "max_y"}
        )
        if set(manifest.get("columns", {})) != expected_columns:
            raise ValueError(f"{operation} calibration candidate columns differ")
        for row in manifest["columns"].values():
            column = resolved.parent / row["path"]
            bound = binding(column)
            if row.get("dtype") != "float32" or row.get("shape") != [count] \
                    or row.get("bytes") != bound["bytes"] \
                    or row.get("sha256") != bound["sha256"]:
                raise ValueError(f"{operation} calibration candidate column differs")
        result.append({"manifest": binding(resolved), "query_count": count})
        previous_count = count
        source_sha = current_source
        indexed_identity = current_index
    return result


def worker_command(args, operation: str, manifest: Path, output: Path) -> list[str]:
    return [
        str(args.python), str(args.source_root / "scripts/v4_librts_long_worker.py"),
        "--source-root", str(args.source_root),
        "--arm", "pyoptix", "--endpoint", "prepared", "--operation", operation,
        "--indexed-npz", str(args.indexed_npz),
        "--query-manifest", str(manifest),
        "--native", str(args.native), "--pyoptix-ptx", str(args.pyoptix_ptx),
        "--optix-sdk", args.optix_sdk,
        "--compute-capability", args.compute_capability,
        "--warmups", "1", "--repetitions", "1", "--output", str(output),
    ]


def run_worker(args, operation: str, candidate: dict[str, Any], ordinal: int, root: Path) -> dict[str, Any]:
    directory = root / operation / f"q-{candidate['query_count']}" / f"process-{ordinal}"
    directory.mkdir(parents=True, exist_ok=False)
    result_path = directory / "WORKER_RESULT.json"
    command = worker_command(args, operation, Path(candidate["manifest"]["path"]), result_path)
    write_new(directory / "COMMAND.json", command)
    environment = dict(os.environ)
    environment.update({
        "CUDA_VISIBLE_DEVICES": args.gpu_uuid,
        "PYTHONPATH": os.pathsep.join((str(args.source_root / "src"), str(args.source_root))),
        "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1",
        "CUDA_CACHE_DISABLE": "1", "OPTIX_CACHE_ENABLED": "0", "OPTIX_CACHE_MAXSIZE": "0",
    })
    started = time.perf_counter_ns()
    process = subprocess.Popen(
        command, cwd=args.source_root, env=environment,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True,
    )
    timed_out = False
    try:
        stdout, stderr = process.communicate(timeout=args.worker_timeout_seconds)
    except subprocess.TimeoutExpired:
        timed_out = True
        os.killpg(process.pid, signal.SIGKILL)
        stdout, stderr = process.communicate()
    ended = time.perf_counter_ns()
    (directory / "STDOUT.bin").write_bytes(stdout)
    (directory / "STDERR.bin").write_bytes(stderr)
    exit_record = {
        "returncode": process.returncode, "timed_out": timed_out,
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
    expected = read_json(candidate["manifest"]["path"])
    samples = worker.get("samples_ns") if worker is not None else None
    valid = not timed_out and process.returncode == 0 and worker is not None \
        and worker.get("status") == "PASS__LIBRTS_LONG_QUERY_WORKER" \
        and worker.get("arm") == "pyoptix" and worker.get("operation") == operation \
        and worker.get("endpoint") == "prepared" \
        and worker.get("query_count") == candidate["query_count"] \
        and worker.get("expected_count_u64") == expected["expected_count_u64"] \
        and worker.get("all_queries_distinct") is True \
        and worker.get("source", {}).get("commit") == args.source_commit \
        and worker.get("source", {}).get("tree") == args.source_tree \
        and worker.get("source", {}).get("dirty") is False \
        and worker.get("machine", {}).get("gpu", {}).get("uuid") == args.gpu_uuid \
        and worker.get("warmup_count") == 1 and worker.get("timed_repetition_count") == 1 \
        and isinstance(samples, list) and len(samples) == 1 \
        and type(samples[0]) is int and samples[0] > 0 \
        and worker.get("median_ns") == samples[0] \
        and all(int(row.get("count", -1)) == expected["expected_count_u64"] for row in worker.get("outputs", ())) \
        and len(worker.get("outputs", ())) == 1
    record = {
        "operation": operation, "query_count": candidate["query_count"],
        "process_ordinal": ordinal, **exit_record, "worker_contract_validated": valid,
        "command": binding(directory / "COMMAND.json"),
        "stdout": binding(directory / "STDOUT.bin"), "stderr": binding(directory / "STDERR.bin"),
        "exit": binding(directory / "EXIT.json"),
        "worker_result": binding(result_path) if result_path.is_file() else None,
        "worker_parse_error": worker_parse_error,
        "sample_ns": samples[0] if valid else None,
    }
    return record


def calibrate(args) -> dict[str, Any]:
    args.source_root = args.source_root.resolve(strict=True)
    if args.source_root != ROOT or git(args.source_root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError("LibRTS C-only calibration requires this clean source root")
    args.source_commit = git(args.source_root, "rev-parse", "HEAD")
    args.source_tree = git(args.source_root, "rev-parse", "HEAD^{tree}")
    for name in ("python", "indexed_npz", "native", "pyoptix_ptx"):
        setattr(args, name, getattr(args, name).resolve(strict=True))
    point = validate_candidates(args.point_candidate, OPERATIONS[0])
    range_ = validate_candidates(args.range_candidate, OPERATIONS[1])
    indexed_sha = binding(args.indexed_npz)["sha256"]
    selected_index_identities = []
    for candidate in (*point, *range_):
        manifest = read_json(candidate["manifest"]["path"])
        selected_index_identities.append(manifest.get("indexed_identity"))
        if manifest.get("indexed_identity", {}).get("indexed_npz_sha256") != indexed_sha:
            raise ValueError("LibRTS calibration candidate indexed identity differs")
    if any(value != selected_index_identities[0] for value in selected_index_identities[1:]):
        raise ValueError("LibRTS calibration candidates do not share one indexed identity")
    output = args.output.resolve()
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=True)
    schedule = {
        "schema": f"{SCHEMA}.schedule", "status": "FROZEN_BEFORE_C_WORKER_ZERO",
        "source_commit": args.source_commit, "source_tree": args.source_tree,
        "python": binding(args.python), "indexed_npz": binding(args.indexed_npz),
        "native": binding(args.native), "pyoptix_ptx": binding(args.pyoptix_ptx),
        "gpu_uuid": args.gpu_uuid, "processes_per_scale": FRESH_PROCESSES_PER_SCALE,
        "selection_rule": "first increasing candidate with median single natural action >= 1 second",
        "point_candidates": point, "range_candidates": range_,
        "rtdl_workers_authorized": False,
    }
    write_new(output / "SCHEDULE.json", schedule)
    journal = output / "JOURNAL.jsonl"
    records = []
    selected: dict[str, dict[str, Any]] = {}
    try:
        for operation, candidates in zip(OPERATIONS, (point, range_), strict=True):
            for candidate in candidates:
                candidate_records = []
                for ordinal in range(FRESH_PROCESSES_PER_SCALE):
                    record = run_worker(args, operation, candidate, ordinal, output / "workers")
                    records.append(record)
                    candidate_records.append(record)
                    append_journal(journal, record)
                    if not record["worker_contract_validated"]:
                        raise RuntimeError(f"C-only calibration worker failed: {record}")
                samples = [row["sample_ns"] for row in candidate_records]
                median_ns = int(statistics.median(samples))
                if median_ns >= 1_000_000_000:
                    selected[operation] = {
                        "manifest": candidate["manifest"], "query_count": candidate["query_count"],
                        "samples_ns": samples, "median_ns": median_ns,
                        "median_seconds": median_ns / 1e9,
                    }
                    break
            if operation not in selected:
                raise RuntimeError(f"no {operation} candidate reached one second")
    except BaseException as error:
        write_new(output / "FAILURE.json", {
            "schema": SCHEMA, "status": "FAIL__C_ONLY_LIBRTS_LONG_SCALE_NOT_SELECTED",
            "error_type": type(error).__name__, "error": str(error),
            "traceback": traceback.format_exc(), "completed_worker_count": len(records),
            "records": records, "rtdl_worker_count": 0,
        })
        raise
    result = {
        "schema": SCHEMA, "status": "PASS__C_ONLY_LIBRTS_LONG_SCALE_SELECTED",
        "source_commit": args.source_commit, "source_tree": args.source_tree,
        "schedule": binding(output / "SCHEDULE.json"),
        "point_manifest_sha256": selected[OPERATIONS[0]]["manifest"]["sha256"],
        "range_manifest_sha256": selected[OPERATIONS[1]]["manifest"]["sha256"],
        OPERATIONS[0]: selected[OPERATIONS[0]], OPERATIONS[1]: selected[OPERATIONS[1]],
        "completed_worker_count": len(records), "rtdl_worker_count": 0,
        "records": records,
        "selected_scale_median_rule_verified": True,
        "public_claim_authorized": False,
    }
    write_new(output / "CALIBRATION.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--python", type=Path, required=True)
    parser.add_argument("--gpu-uuid", required=True)
    parser.add_argument("--indexed-npz", type=Path, required=True)
    parser.add_argument("--point-candidate", action="append", type=Path, required=True)
    parser.add_argument("--range-candidate", action="append", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--pyoptix-ptx", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--worker-timeout-seconds", type=int, default=900)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = calibrate(args)
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
