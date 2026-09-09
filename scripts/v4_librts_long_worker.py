#!/usr/bin/env python3
"""Run one create-only RTDL or public-PyOptiX LibRTS long-query worker."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
import traceback
from typing import Any


def _sha(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_new(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _gpu() -> dict[str, str]:
    completed = subprocess.run(
        [
            "nvidia-smi", "--query-gpu=name,uuid,compute_cap,driver_version",
            "--format=csv,noheader,nounits",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(f"nvidia-smi failed: {completed.stderr.strip()}")
    rows = [row.strip() for row in completed.stdout.splitlines() if row.strip()]
    if len(rows) != 1:
        raise RuntimeError(f"worker requires exactly one visible GPU: {rows!r}")
    values = [value.strip() for value in rows[0].split(",")]
    if len(values) != 4:
        raise RuntimeError(f"unexpected nvidia-smi row: {rows[0]!r}")
    return dict(zip(("name", "uuid", "compute_capability", "driver"), values))


def _source(source_root: Path) -> dict[str, Any]:
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=source_root, text=True,
            capture_output=True, check=True,
        ).stdout.strip()

    return {
        "commit": git("rev-parse", "HEAD"),
        "tree": git("rev-parse", "HEAD^{tree}"),
        "dirty": bool(git("status", "--porcelain=v1", "--untracked-files=all")),
        "worker_sha256": _sha(Path(__file__).resolve()),
    }


def _load_indexed(path: Path):
    import numpy as np

    with np.load(path, allow_pickle=False) as arrays:
        result = {
            name: np.ascontiguousarray(arrays[name], dtype=np.float32)
            for name in ("min_x", "min_y", "max_x", "max_y")
        }
    count = int(result["min_x"].size)
    if count <= 0 or any(column.size != count for column in result.values()):
        raise ValueError("indexed NPZ has invalid AABB column cardinality")
    if any(not bool(np.isfinite(column).all()) for column in result.values()):
        raise ValueError("indexed NPZ contains nonfinite AABB coordinates")
    if bool((result["max_x"] < result["min_x"]).any()) or bool(
        (result["max_y"] < result["min_y"]).any()
    ):
        raise ValueError("indexed NPZ contains inverted AABB bounds")
    return result


def _prepare_rtdl(args, indexed, columns, expected: int, chunk_rows: int | None):
    from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile

    app = _load_module(
        args.source_root / "Paper-reproduction-apps/librts-paper/v4_whole_app.py",
        "v4_librts_long_worker_app",
    )
    native_sha256 = _sha(args.native)
    os.environ["RTDL_OPTIX_LIB"] = str(args.native)
    os.environ["RTDL_OPTIX_LIBRARY"] = str(args.native)
    target = ReferenceTargetProfile(
        provider="optix",
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
        native_sha256=native_sha256,
        supports_custom_aabb=True,
        supports_builtin_triangle=True,
    )
    owner = app.prepare_v4_real_scale_count(
        target=target,
        indexed_columns=indexed,
        operation=args.operation,
        native_library_path=args.native,
    )
    if chunk_rows is None:
        if args.operation == "point_contains":
            owner.bind_query_columns(point_columns=columns)
        else:
            owner.bind_query_columns(box_columns=columns)
        query_layout = owner.lifecycle_receipt["prepared_query_layout"]
        if query_layout != "device_f32_soa":
            raise RuntimeError(
                f"RTDL LibRTS requires device_f32_soa queries, observed {query_layout!r}"
            )
    else:
        query_layout = "device_f32_soa_per_chunk"

    def execute() -> dict[str, Any]:
        if chunk_rows is None:
            result = owner.execute_count()
            receipts = (result.get("traversal_receipt"),)
        else:
            kwargs = (
                {"point_columns": columns}
                if args.operation == "point_contains"
                else {"box_columns": columns}
            )
            result = owner.execute_count_query_column_stream(
                **kwargs, chunk_rows=chunk_rows
            )
            receipts = tuple(result.get("traversal_receipts", ()))
        value = int(result["count"])
        if value != expected:
            raise RuntimeError(
                f"RTDL LibRTS oracle mismatch: expected={expected} observed={value}"
            )
        if not receipts or any(
            not isinstance(receipt, Mapping)
            or receipt.get("physical_executor_classification")
            != "optix_traversal_observed"
            for receipt in receipts
        ):
            raise RuntimeError("RTDL LibRTS execution lacks validated OptiX receipt")
        return {
            "count": value,
            "chunk_count": len(receipts),
            "receipt_sha256": [
                receipt.get("receipt_sha256") for receipt in receipts
            ],
            "physical_executor_classification": "optix_traversal_observed",
        }

    return owner, execute, {
        "path": (
            "public_v4_verified_aabb_relation_count_device_f32_soa"
            if chunk_rows is None
            else "public_v4_verified_aabb_relation_count_streamed_device_f32_soa"
        ),
        "native_sha256": native_sha256,
        "query_gas_built": False,
        "device_query_layout": query_layout,
        "stream_chunk_rows": chunk_rows,
        "query_validation_and_h2d_inside_action": chunk_rows is not None,
    }


def _prepare_pyoptix(args, indexed, columns, expected: int, chunk_rows: int | None):
    from experiments.v4_paper_apps_pyoptix.librts_owner import (
        PublicPyOptixLibRTSCountOwner,
    )

    ptx = args.pyoptix_ptx.read_bytes()
    owner = PublicPyOptixLibRTSCountOwner.prepare(indexed, prebuilt_ptx=ptx)
    if chunk_rows is None:
        owner.bind_query_columns(operation=args.operation, columns=columns)
        if owner.query_layout != "device_f32_soa":
            raise RuntimeError(
                f"PyOptiX LibRTS requires device_f32_soa queries, observed {owner.query_layout!r}"
            )
        query_layout = owner.query_layout
    else:
        query_layout = "device_f32_soa_per_chunk"

    def execute() -> dict[str, Any]:
        if chunk_rows is None:
            result = owner.execute_count(
                operation=args.operation,
                expected_count=expected,
            )
            chunk_count = 1
        else:
            result = owner.execute_count_query_column_stream(
                operation=args.operation,
                columns=columns,
                chunk_rows=chunk_rows,
                expected_count=expected,
            )
            chunk_count = len(result.chunk_counts)
        return {
            "count": int(result.checked_u64),
            "chunk_count": chunk_count,
            "device_status": (
                int(result.device_status)
                if chunk_rows is None
                else list(result.device_statuses)
            ),
        }

    return owner, execute, {
        "path": (
            "public_pyoptix_custom_aabb_device_f32_soa"
            if chunk_rows is None
            else "public_pyoptix_custom_aabb_streamed_device_f32_soa"
        ),
        "ptx_sha256": hashlib.sha256(ptx).hexdigest(),
        "query_gas_built": False,
        "device_query_layout": query_layout,
        "stream_chunk_rows": chunk_rows,
        "query_validation_and_h2d_inside_action": chunk_rows is not None,
    }


def run(args) -> dict[str, Any]:
    from experiments.v4_librts_long_workload.query_grid import load_query_columns

    if args.repetitions <= 0 or args.warmups < 0:
        raise ValueError("repetitions must be positive and warmups nonnegative")
    if args.endpoint == "complete" and (
        args.repetitions != 1 or args.warmups != 0
    ):
        raise ValueError("complete endpoint requires one repetition and no warmup")
    input_started = time.perf_counter_ns()
    indexed = _load_indexed(args.indexed_npz)
    columns, manifest = load_query_columns(args.query_manifest)
    if manifest["operation"] != args.operation:
        raise ValueError("query manifest operation differs from worker operation")
    expected = int(manifest["expected_count_u64"])
    streaming = manifest.get("streaming", {})
    chunk_rows = streaming.get("chunk_rows") if streaming.get("enabled") else None
    if chunk_rows is not None:
        expected_chunks = (
            int(manifest["query_count"]) + int(chunk_rows) - 1
        ) // int(chunk_rows)
        if type(chunk_rows) is not int or not 0 < chunk_rows <= 0xFFFFFFFF \
                or streaming.get("chunk_count") != expected_chunks \
                or streaming.get("partition") \
                != "contiguous_nonoverlapping_full_cover" \
                or streaming.get("query_validation_and_h2d_inside_action") is not True:
            raise ValueError("query manifest streaming contract differs")
    input_ended = time.perf_counter_ns()

    prepare_started = time.perf_counter_ns()
    if args.arm == "rtdl":
        owner, execute, method = _prepare_rtdl(
            args, indexed, columns, expected, chunk_rows
        )
    else:
        owner, execute, method = _prepare_pyoptix(
            args, indexed, columns, expected, chunk_rows
        )
    prepare_ended = time.perf_counter_ns()
    warmup_outputs = []
    samples = []
    outputs = []
    close_started = None
    close_ended = None
    try:
        for _ in range(args.warmups):
            warmup_outputs.append(execute())
        for _ in range(args.repetitions):
            started = time.perf_counter_ns()
            output = execute()
            ended = time.perf_counter_ns()
            if ended <= started or int(output["count"]) != expected:
                raise RuntimeError("timed LibRTS execution failed its output contract")
            samples.append(ended - started)
            outputs.append(output)
    finally:
        close_started = time.perf_counter_ns()
        owner.close()
        close_ended = time.perf_counter_ns()
    median_ns = int(statistics.median(samples))
    complete_task_ns = (
        prepare_ended - prepare_started + samples[0] + close_ended - close_started
        if args.endpoint == "complete"
        else None
    )
    return {
        "schema": "rtdl.v4.librts.long_query_worker.v1",
        "status": "PASS__LIBRTS_LONG_QUERY_WORKER",
        "arm": args.arm,
        "endpoint": args.endpoint,
        "operation": args.operation,
        "query_count": int(manifest["query_count"]),
        "indexed_count": int(indexed["min_x"].size),
        "expected_count_u64": expected,
        "mean_hits_per_query": float(manifest["mean_hits_per_query"]),
        "all_queries_distinct": bool(manifest["all_queries_distinct"]),
        "streaming": streaming,
        "samples_ns": samples,
        "median_ns": median_ns,
        "queries_per_second_at_median": int(manifest["query_count"]) / (median_ns / 1e9),
        "input_load_and_digest_ns": input_ended - input_started,
        "prepare_and_bind_ns": prepare_ended - prepare_started,
        "close_ns": close_ended - close_started,
        "complete_task_ns": complete_task_ns,
        "warmup_count": len(warmup_outputs),
        "timed_repetition_count": len(samples),
        "outputs": outputs,
        "method": method,
        "input_identity": {
            "indexed_npz": str(args.indexed_npz),
            "indexed_npz_sha256": _sha(args.indexed_npz),
            "query_manifest": str(args.query_manifest),
            "query_manifest_sha256": _sha(args.query_manifest),
            "source_query_sha256": manifest["source_query_sha256"],
            "oracle": manifest["oracle"],
        },
        "machine": {
            "hostname": platform.node(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "python_executable": str(Path(sys.executable).resolve()),
            "gpu": _gpu(),
        },
        "source": _source(args.source_root),
        "timing_boundary": {
            "action_includes": [
                "public_execute_entry",
                *(
                    [
                        "query_chunk_validation_and_h2d",
                        "contiguous_nonoverlapping_full_query_cover",
                    ]
                    if chunk_rows is not None
                    else []
                ),
                "optix_launch",
                "device_u32_to_u64_reduction",
                "stream_synchronization",
                "device_status_check",
                "checked_scalar_return",
                "expected_scalar_check",
            ],
            "action_excludes": [
                "input_file_load_and_digest",
                "indexed_gas_prepare",
                *(["query_column_upload"] if chunk_rows is None else []),
                "untimed_warmup",
                "close",
            ],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--arm", choices=("rtdl", "pyoptix"), required=True)
    parser.add_argument(
        "--endpoint", choices=("complete", "prepared"), default="prepared"
    )
    parser.add_argument(
        "--operation", choices=("point_contains", "range_contains"), required=True
    )
    parser.add_argument("--indexed-npz", type=Path, required=True)
    parser.add_argument("--query-manifest", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--pyoptix-ptx", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--warmups", type=int, default=1)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.source_root = args.source_root.resolve(strict=True)
    args.indexed_npz = args.indexed_npz.resolve(strict=True)
    args.query_manifest = args.query_manifest.resolve(strict=True)
    args.native = args.native.resolve(strict=True)
    args.pyoptix_ptx = args.pyoptix_ptx.resolve(strict=True)
    args.output = args.output.resolve()
    try:
        payload = run(args)
        exit_code = 0
    except BaseException as error:
        payload = {
            "schema": "rtdl.v4.librts.long_query_worker.v1",
            "status": "FAIL__LIBRTS_LONG_QUERY_WORKER",
            "arm": args.arm,
            "endpoint": args.endpoint,
            "operation": args.operation,
            "error_type": type(error).__name__,
            "error": str(error),
            "traceback": traceback.format_exc(),
        }
        exit_code = 1
    _write_new(args.output, payload)
    print(json.dumps(payload, indent=2, sort_keys=True, allow_nan=False))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
