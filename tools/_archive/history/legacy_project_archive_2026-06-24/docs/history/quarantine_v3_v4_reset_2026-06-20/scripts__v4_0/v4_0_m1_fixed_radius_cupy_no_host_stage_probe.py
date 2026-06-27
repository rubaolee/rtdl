#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COUNTER_SOURCE = ROOT / "src/native/tools/rtdl_cuda_transfer_counter.c"
DEFAULT_COUNTER_LIBRARY = ROOT / "build/librtdl_cuda_transfer_counter.so"


def _ensure_transfer_counter_preloaded(library: Path, source: Path) -> dict[str, object]:
    library = library.resolve()
    source = source.resolve()
    preload = os.environ.get("LD_PRELOAD", "")
    preload_parts = [part for part in preload.split(os.pathsep) if part]
    already_preloaded = str(library) in preload_parts
    os.environ["RTDL_CUDA_TRANSFER_COUNTER_LIBRARY"] = str(library)
    build = {
        "skipped": True,
        "reason": "already_preloaded",
        "library_exists": library.exists(),
    }
    if not already_preloaded:
        build = _build_transfer_counter(library, source)
        os.environ["LD_PRELOAD"] = os.pathsep.join([str(library), *preload_parts])
        os.environ["RTDL_CUDA_TRANSFER_COUNTER_REEXEC"] = "1"
        os.execvpe(sys.executable, [sys.executable, *sys.argv], os.environ.copy())
    return {
        "library": str(library),
        "source": str(source),
        "already_preloaded": already_preloaded,
        "build": build,
        "ld_preload": os.environ.get("LD_PRELOAD", ""),
    }


def _build_transfer_counter(library: Path, source: Path) -> dict[str, object]:
    if not source.exists():
        raise FileNotFoundError(f"transfer counter source not found: {source}")
    library.parent.mkdir(parents=True, exist_ok=True)
    command = [
        os.environ.get("CC", "cc"),
        "-shared",
        "-fPIC",
        "-O2",
        "-std=c11",
        str(source),
        "-ldl",
        "-o",
        str(library),
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    if completed.returncode != 0:
        raise RuntimeError(
            "failed to build CUDA transfer counter:\n"
            + (completed.stdout or "")
            + (completed.stderr or "")
        )
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


_TRANSFER_COUNTER_BOOTSTRAP = _ensure_transfer_counter_preloaded(
    Path(os.environ.get("RTDL_CUDA_TRANSFER_COUNTER_LIBRARY", DEFAULT_COUNTER_LIBRARY)),
    Path(os.environ.get("RTDL_CUDA_TRANSFER_COUNTER_SOURCE", DEFAULT_COUNTER_SOURCE)),
)

import cupy as cp
import rtdsl
from rtdsl import CudaTransferCounter


def _columns_from_xy(ids: np.ndarray, xy: np.ndarray) -> dict[str, object]:
    return {
        "ids": cp.asarray(ids.astype(np.uint32, copy=False)),
        "x": cp.asarray(xy[:, 0].astype(np.float64, copy=False)),
        "y": cp.asarray(xy[:, 1].astype(np.float64, copy=False)),
    }


def _outputs(count: int) -> dict[str, object]:
    return {
        "query_ids": cp.zeros((count,), dtype=cp.uint32),
        "neighbor_counts": cp.zeros((count,), dtype=cp.uint32),
        "threshold_flags": cp.zeros((count,), dtype=cp.uint32),
    }


def _make_case(point_count: int) -> tuple[dict[str, object], dict[str, object]]:
    rng = np.random.default_rng(404)
    search_xy = rng.uniform(-1.0, 1.0, size=(point_count, 2))
    jitter = rng.normal(0.0, 0.02, size=(point_count, 2))
    query_xy = search_xy + jitter
    ids = np.arange(point_count, dtype=np.uint32)
    search = _columns_from_xy(ids + np.uint32(10), search_xy)
    query = _columns_from_xy(ids + np.uint32(1), query_xy)
    return query, search


def _named_column_min_bytes(point_count: int) -> int:
    return min(
        int(point_count) * np.dtype(np.uint32).itemsize,
        int(point_count) * np.dtype(np.float64).itemsize,
    )


def _classify_snapshot(
    snapshot: dict[str, object],
    *,
    point_count: int,
    allowed_non_column_host_to_device_bytes: int,
) -> dict[str, object]:
    h2d = int(snapshot.get("host_to_device_bytes", 0) or 0)
    d2h_calls = int(snapshot.get("device_to_host_calls", 0) or 0)
    unknown_calls = int(snapshot.get("unknown_calls", 0) or 0)
    min_named_column_bytes = _named_column_min_bytes(point_count)
    disallowed = []
    if d2h_calls:
        disallowed.append("device_to_host_copy_observed")
    if unknown_calls:
        disallowed.append("unknown_direction_copy_observed")
    if h2d > int(allowed_non_column_host_to_device_bytes):
        disallowed.append("host_to_device_bytes_exceed_allowed_launch_parameter_scope")
    if h2d >= min_named_column_bytes:
        disallowed.append("host_to_device_bytes_reach_named_column_size")
    return {
        "transfer_counter_observed": True,
        "measured_window": "v4_m1_fixed_radius_prepare_plus_query_after_warmup",
        "allowed_non_column_host_to_device_bytes": int(allowed_non_column_host_to_device_bytes),
        "min_named_column_bytes": min_named_column_bytes,
        "observed_total_calls": int(snapshot.get("total_calls", 0) or 0),
        "observed_total_bytes": int(snapshot.get("total_bytes", 0) or 0),
        "observed_host_to_device_calls": int(snapshot.get("host_to_device_calls", 0) or 0),
        "observed_host_to_device_bytes": h2d,
        "observed_device_to_host_calls": d2h_calls,
        "observed_device_to_host_bytes": int(snapshot.get("device_to_host_bytes", 0) or 0),
        "observed_device_to_device_calls": int(snapshot.get("device_to_device_calls", 0) or 0),
        "observed_device_to_device_bytes": int(snapshot.get("device_to_device_bytes", 0) or 0),
        "observed_unknown_calls": unknown_calls,
        "observed_unknown_bytes": int(snapshot.get("unknown_bytes", 0) or 0),
        "internal_device_to_device_copy_allowed": True,
        "internal_device_to_device_scope": "device-resident AABB/BVH staging, not host staging",
        "host_stage_observed": bool(disallowed),
        "disallowed_reasons": disallowed,
        "no_host_stage_ready": not disallowed,
        "v4_true_zero_copy_claim_authorized": False,
    }


def run_probe(
    *,
    point_count: int,
    radius: float,
    threshold: int,
    allowed_non_column_host_to_device_bytes: int,
    transfer_counter_library: Path,
) -> dict[str, object]:
    query, search = _make_case(int(point_count))
    warmup_outputs = _outputs(int(point_count))
    warmup_stream = cp.cuda.Stream(non_blocking=True)
    with warmup_stream:
        rtdsl.run_v4_fixed_radius_count_threshold_2d(
            query,
            search,
            radius=radius,
            threshold=threshold,
            partner="cupy",
            output_columns=warmup_outputs,
            stream=warmup_stream.ptr,
            return_metadata=True,
        )
    warmup_stream.synchronize()

    outputs = _outputs(int(point_count))
    stream = cp.cuda.Stream(non_blocking=True)
    counter = CudaTransferCounter(transfer_counter_library)
    counter.reset()
    counter.enable()
    try:
        with stream:
            result = rtdsl.run_v4_fixed_radius_count_threshold_2d(
                query,
                search,
                radius=radius,
                threshold=threshold,
                partner="cupy",
                output_columns=outputs,
                stream=stream.ptr,
                return_metadata=True,
            )
        stream.synchronize()
        snapshot = counter.disable_and_snapshot()
    except Exception:
        counter.disable_and_snapshot()
        raise

    classification = _classify_snapshot(
        snapshot,
        point_count=int(point_count),
        allowed_non_column_host_to_device_bytes=int(allowed_non_column_host_to_device_bytes),
    )
    if not classification["no_host_stage_ready"]:
        raise AssertionError(f"V4 M1 no-host-stage probe failed: {classification!r}")
    metadata = dict(result["metadata"])
    return {
        "status": "pass-with-boundary",
        "route_id": "fixed_radius_count_threshold_2d",
        "point_count": int(point_count),
        "radius": float(radius),
        "threshold": int(threshold),
        "metadata_subset": {
            "caller_stream_handle_nonzero": int(metadata["caller_stream_handle"]) != 0,
            "prepare_stream_handle_nonzero": int(metadata["prepare_stream_handle"]) != 0,
            "native_prepare_stream_propagation_ready": bool(
                metadata["native_prepare_stream_propagation_ready"]
            ),
            "native_call_device_pointer_echo_complete": bool(
                metadata["native_call_device_pointer_echo_complete"]
            ),
            "named_cuda_columns_no_host_stage_authorized": bool(
                metadata["named_cuda_columns_no_host_stage_authorized"]
            ),
            "internal_device_staging_disclosed": bool(metadata["internal_device_staging_disclosed"]),
            "native_async_ready": bool(metadata["native_async_ready"]),
            "v4_true_zero_copy_claim_authorized": bool(
                metadata["v4_true_zero_copy_claim_authorized"]
            ),
        },
        "transfer_counter_snapshot": snapshot,
        "transfer_counter_classification": classification,
        "claim_boundaries": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "v4_true_zero_copy_claim_authorized": False,
            "async_claim_authorized": False,
            "reason": (
                "This proves no observed host-stage copy of named search/query/output columns in the "
                "measured V4 M1 prepare-plus-query window after warmup. Internal device-to-device "
                "AABB/BVH staging is present, so this authorizes named-column no-host-stage wording, "
                "not public end-to-end true-zero-copy wording."
            ),
        },
        "runner_transfer_counter_bootstrap": dict(_TRANSFER_COUNTER_BOOTSTRAP),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the V4 M1 no-host-stage transfer-counter probe.")
    parser.add_argument("--point-count", type=int, default=4096)
    parser.add_argument("--radius", type=float, default=0.05)
    parser.add_argument("--threshold", type=int, default=1)
    parser.add_argument("--allowed-non-column-host-to-device-bytes", type=int, default=4096)
    parser.add_argument(
        "--transfer-counter-library",
        type=Path,
        default=Path(os.environ["RTDL_CUDA_TRANSFER_COUNTER_LIBRARY"]),
    )
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    args = parser.parse_args()

    result = run_probe(
        point_count=args.point_count,
        radius=args.radius,
        threshold=args.threshold,
        allowed_non_column_host_to_device_bytes=args.allowed_non_column_host_to_device_bytes,
        transfer_counter_library=args.transfer_counter_library,
    )
    text = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
