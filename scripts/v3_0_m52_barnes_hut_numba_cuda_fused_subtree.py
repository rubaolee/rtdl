from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import statistics
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.current.apps.simulation import rtdl_barnes_hut_force_app as app
from rtdsl.numba_partner_continuation import configure_numba_cuda_toolchain_environment
from scripts.goal2544_barnes_hut_torch_cuda_subtree_containment import _prepare_subtree_arrays


GOAL = "Goal4448 / V3.0 M52 - Barnes-Hut Numba CUDA fused subtree prototype"
VERSION = "rtdl.v3_0.barnes_hut_numba_cuda_fused_subtree.goal4448.v1"
MODE = "numba_cuda_fused_subtree_force_sum_prototype"
COMPARISON_THETA = 0.5
COMPARISON_MAX_DEPTH = 32

# Checked-in M41/M42/M45 rows. These constants are explanatory baselines only;
# the script's measured rows remain the source of truth for this M52 run.
M45_CPU_FUSED_SECONDS = {
    8192: 0.0013038069009780884,
    16384: 0.004121541976928711,
    32768: 0.01516096293926239,
}
M41_PREPARED_OPTIX_NUMBA_SECONDS = {
    8192: 0.014712025072696686,
    16384: 0.030269341140293123,
    32768: 0.0825402173339386,
}
M42_APP_MODE_OPTIX_NUMBA_SECONDS = {
    8192: 0.016139463325687407,
}

_NUMBA_CUDA_FUSED_SUBTREE_KERNEL = None


def _parse_body_counts(raw: str) -> tuple[int, ...]:
    values = tuple(int(part.strip()) for part in raw.split(",") if part.strip())
    if not values:
        raise ValueError("--body-counts must include at least one positive integer")
    for value in values:
        if value <= 0:
            raise ValueError("--body-counts values must be positive")
    return values


def _median(values: list[float]) -> float:
    if not values:
        return 0.0
    return float(statistics.median(values))


def _numba_cuda_fused_subtree_kernel(cuda: Any) -> Any:
    global _NUMBA_CUDA_FUSED_SUBTREE_KERNEL
    if _NUMBA_CUDA_FUSED_SUBTREE_KERNEL is not None:
        return _NUMBA_CUDA_FUSED_SUBTREE_KERNEL

    @cuda.jit
    def kernel(
        point_x,
        point_y,
        point_mass,
        node_cx,
        node_cy,
        node_half_size,
        node_mass,
        node_resume_index,
        node_subtree_end_index,
        source_leaf_node_index,
        member_offsets,
        member_indices,
        child_offsets,
        child_indices,
        theta,
        softening,
        out_x,
        out_y,
        out_visited,
        out_aggregate,
        out_exact,
        status,
    ):
        source_index = cuda.grid(1)
        source_count = point_x.shape[0]
        if source_index >= source_count:
            return

        node_count = node_cx.shape[0]
        if node_count < 1:
            cuda.atomic.max(status, 0, 1)
            return

        source_leaf = source_leaf_node_index[source_index]
        if source_leaf < 0 or source_leaf >= node_count:
            cuda.atomic.max(status, 0, 4)
            return

        sx = point_x[source_index]
        sy = point_y[source_index]
        smass = point_mass[source_index]
        softening_sq = softening * softening
        sum_x = 0.0
        sum_y = 0.0
        visited = 0
        aggregate_count = 0
        exact_count = 0
        node_index = 0

        while node_index >= 0:
            if node_index >= node_count:
                cuda.atomic.max(status, 0, 2)
                return
            visited += 1
            dx_node = node_cx[node_index] - sx
            dy_node = node_cy[node_index] - sy
            distance = math.sqrt(dx_node * dx_node + dy_node * dy_node)
            if distance == 0.0:
                opening_ratio = 1.0e300
            else:
                opening_ratio = (2.0 * node_half_size[node_index]) / distance

            subtree_end = node_subtree_end_index[node_index]
            contains_source = node_index <= source_leaf and source_leaf < subtree_end

            if (not contains_source) and opening_ratio < theta:
                dist_sq = dx_node * dx_node + dy_node * dy_node + softening_sq
                if dist_sq != 0.0:
                    inv_dist = 1.0 / math.sqrt(dist_sq)
                    scale = smass * node_mass[node_index] * inv_dist * inv_dist * inv_dist
                    sum_x += dx_node * scale
                    sum_y += dy_node * scale
                aggregate_count += 1
                node_index = node_resume_index[node_index]
                continue

            child_begin = child_offsets[node_index]
            child_end = child_offsets[node_index + 1]
            if child_begin < child_end:
                node_index = child_indices[child_begin]
                continue

            member_begin = member_offsets[node_index]
            member_end = member_offsets[node_index + 1]
            for offset in range(member_begin, member_end):
                target_index = member_indices[offset]
                if target_index == source_index:
                    continue
                dx = point_x[target_index] - sx
                dy = point_y[target_index] - sy
                dist_sq = dx * dx + dy * dy + softening_sq
                if dist_sq != 0.0:
                    inv_dist = 1.0 / math.sqrt(dist_sq)
                    scale = smass * point_mass[target_index] * inv_dist * inv_dist * inv_dist
                    sum_x += dx * scale
                    sum_y += dy * scale
                exact_count += 1
            node_index = node_resume_index[node_index]

        out_x[source_index] = sum_x
        out_y[source_index] = sum_y
        out_visited[source_index] = visited
        out_aggregate[source_index] = aggregate_count
        out_exact[source_index] = exact_count

    _NUMBA_CUDA_FUSED_SUBTREE_KERNEL = kernel
    return kernel


def _device_inputs(prepared: dict[str, Any], np: Any, cuda: Any) -> tuple[dict[str, Any], dict[str, float]]:
    transfer_start = time.perf_counter()
    host_arrays = {
        "point_x": np.asarray(prepared["point_x"], dtype=np.float64),
        "point_y": np.asarray(prepared["point_y"], dtype=np.float64),
        "point_mass": np.asarray(prepared["point_mass"], dtype=np.float64),
        "node_cx": np.asarray(prepared["node_cx"], dtype=np.float64),
        "node_cy": np.asarray(prepared["node_cy"], dtype=np.float64),
        "node_half_size": np.asarray(prepared["node_half_size"], dtype=np.float64),
        "node_mass": np.asarray(prepared["node_mass"], dtype=np.float64),
        "node_resume_index": np.asarray(prepared["node_resume_index"], dtype=np.int64),
        "node_subtree_end_index": np.asarray(prepared["node_subtree_end_index"], dtype=np.int64),
        "source_leaf_node_index": np.asarray(prepared["source_leaf_node_index"], dtype=np.int64),
        "member_offsets": np.asarray(prepared["member_offsets"], dtype=np.int64),
        "member_indices": np.asarray(prepared["member_indices"], dtype=np.int64),
        "child_offsets": np.asarray(prepared["child_offsets"], dtype=np.int64),
        "child_indices": np.asarray(prepared["child_indices"], dtype=np.int64),
    }
    device_arrays = {name: cuda.to_device(values) for name, values in host_arrays.items()}
    cuda.synchronize()
    return device_arrays, {
        "host_array_count": float(len(host_arrays)),
        "host_to_device_wall_sec": time.perf_counter() - transfer_start,
    }


def _launch_kernel(
    *,
    kernel: Any,
    cuda: Any,
    stream: Any,
    blocks: int,
    threads: int,
    device_arrays: dict[str, Any],
    theta: float,
    softening: float,
    out_x: Any,
    out_y: Any,
    out_visited: Any,
    out_aggregate: Any,
    out_exact: Any,
    status: Any,
) -> None:
    kernel[blocks, threads, stream](
        device_arrays["point_x"],
        device_arrays["point_y"],
        device_arrays["point_mass"],
        device_arrays["node_cx"],
        device_arrays["node_cy"],
        device_arrays["node_half_size"],
        device_arrays["node_mass"],
        device_arrays["node_resume_index"],
        device_arrays["node_subtree_end_index"],
        device_arrays["source_leaf_node_index"],
        device_arrays["member_offsets"],
        device_arrays["member_indices"],
        device_arrays["child_offsets"],
        device_arrays["child_indices"],
        float(theta),
        float(softening),
        out_x,
        out_y,
        out_visited,
        out_aggregate,
        out_exact,
        status,
    )


def _reset_status(status: Any, np: Any) -> None:
    status.copy_to_device(np.zeros((1,), dtype=np.int32))


def _status_value(status: Any) -> int:
    return int(status.copy_to_host()[0])


def _run_reference_validation(
    *,
    prepared: dict[str, Any],
    force_x: Any,
    force_y: Any,
    theta: float,
    validate: bool,
    validate_max_body_count: int,
) -> dict[str, Any]:
    bodies = tuple(prepared["bodies"])
    if not validate:
        return {"skipped": True, "reason": "not_requested"}
    if len(bodies) > validate_max_body_count:
        return {
            "skipped": True,
            "reason": "body_count_above_validate_max",
            "validate_max_body_count": int(validate_max_body_count),
        }

    reference = rt.sum_aggregate_frontier_weighted_vectors_2d(
        bodies,
        bodies,
        tuple(prepared["tree"]["nodes"]),
        theta=theta,
        softening=app.SOFTENING,
    )
    expected_by_id = {
        int(row["source_id"]): (float(row["vector_x"]), float(row["vector_y"]))
        for row in reference["vector_sum_rows"]
    }
    max_abs_diff_x = max(
        abs(float(force_x[index]) - expected_by_id[int(bodies[index].id)][0])
        for index in range(len(bodies))
    )
    max_abs_diff_y = max(
        abs(float(force_y[index]) - expected_by_id[int(bodies[index].id)][1])
        for index in range(len(bodies))
    )
    passed = max_abs_diff_x <= 1.0e-7 and max_abs_diff_y <= 1.0e-7
    return {
        "skipped": False,
        "compared_against": "sum_aggregate_frontier_weighted_vectors_2d_cpu_reference",
        "tolerance": 1.0e-7,
        "max_abs_diff_x": max_abs_diff_x,
        "max_abs_diff_y": max_abs_diff_y,
        "passed": passed,
        "reference_frontier_row_count": int(reference["summary"]["contribution_row_count"]),
    }


def run_numba_cuda_fused_subtree(
    *,
    body_count: int,
    bucket_size: int,
    max_depth: int,
    theta: float,
    softening: float,
    warmup: int,
    repeats: int,
    threads: int,
    validate: bool,
    validate_max_body_count: int,
) -> dict[str, Any]:
    if warmup < 0:
        raise ValueError("warmup must be non-negative")
    if repeats < 1:
        raise ValueError("repeats must be positive")
    if threads <= 0:
        raise ValueError("threads must be positive")

    run_start = time.perf_counter()
    env = configure_numba_cuda_toolchain_environment()
    import numpy as np
    from numba import cuda

    if not cuda.is_available():
        raise RuntimeError("Numba CUDA fused subtree prototype requires a CUDA-capable pod")
    prepare_start = time.perf_counter()
    prepared = _prepare_subtree_arrays(body_count, bucket_size, max_depth)
    tree_prepare_wall_sec = time.perf_counter() - prepare_start

    source_count = len(prepared["point_x"])
    node_count = len(prepared["node_cx"])
    member_count = len(prepared["member_indices"])
    child_edge_count = len(prepared["child_indices"])
    blocks = (source_count + int(threads) - 1) // int(threads)
    device_arrays, transfer_phases = _device_inputs(prepared, np, cuda)

    out_x = cuda.device_array((source_count,), dtype=np.float64)
    out_y = cuda.device_array((source_count,), dtype=np.float64)
    out_visited = cuda.device_array((source_count,), dtype=np.int64)
    out_aggregate = cuda.device_array((source_count,), dtype=np.int64)
    out_exact = cuda.device_array((source_count,), dtype=np.int64)
    status = cuda.to_device(np.zeros((1,), dtype=np.int32))
    kernel = _numba_cuda_fused_subtree_kernel(cuda)
    stream = cuda.stream()

    compile_start = time.perf_counter()
    _launch_kernel(
        kernel=kernel,
        cuda=cuda,
        stream=stream,
        blocks=blocks,
        threads=int(threads),
        device_arrays=device_arrays,
        theta=theta,
        softening=softening,
        out_x=out_x,
        out_y=out_y,
        out_visited=out_visited,
        out_aggregate=out_aggregate,
        out_exact=out_exact,
        status=status,
    )
    stream.synchronize()
    compile_and_first_launch_wall_sec = time.perf_counter() - compile_start
    first_status = _status_value(status)
    if first_status != 0:
        raise RuntimeError(f"Numba CUDA fused subtree first launch failed with status {first_status}")

    for _ in range(int(warmup)):
        _reset_status(status, np)
        _launch_kernel(
            kernel=kernel,
            cuda=cuda,
            stream=stream,
            blocks=blocks,
            threads=int(threads),
            device_arrays=device_arrays,
            theta=theta,
            softening=softening,
            out_x=out_x,
            out_y=out_y,
            out_visited=out_visited,
            out_aggregate=out_aggregate,
            out_exact=out_exact,
            status=status,
        )
        stream.synchronize()
        warm_status = _status_value(status)
        if warm_status != 0:
            raise RuntimeError(f"Numba CUDA fused subtree warmup failed with status {warm_status}")

    repeat_rows: list[dict[str, float]] = []
    for repeat_index in range(int(repeats)):
        _reset_status(status, np)
        start_event = cuda.event(timing=True)
        end_event = cuda.event(timing=True)
        wall_start = time.perf_counter()
        start_event.record(stream)
        _launch_kernel(
            kernel=kernel,
            cuda=cuda,
            stream=stream,
            blocks=blocks,
            threads=int(threads),
            device_arrays=device_arrays,
            theta=theta,
            softening=softening,
            out_x=out_x,
            out_y=out_y,
            out_visited=out_visited,
            out_aggregate=out_aggregate,
            out_exact=out_exact,
            status=status,
        )
        end_event.record(stream)
        end_event.synchronize()
        wall_sec = time.perf_counter() - wall_start
        repeat_status = _status_value(status)
        if repeat_status != 0:
            raise RuntimeError(
                f"Numba CUDA fused subtree repeat {repeat_index} failed with status {repeat_status}"
            )
        repeat_rows.append(
            {
                "repeat_index": float(repeat_index),
                "kernel_event_ms": float(start_event.elapsed_time(end_event)),
                "kernel_wall_sec": float(wall_sec),
            }
        )

    copy_back_start = time.perf_counter()
    force_x = out_x.copy_to_host()
    force_y = out_y.copy_to_host()
    visited = out_visited.copy_to_host()
    aggregate = out_aggregate.copy_to_host()
    exact = out_exact.copy_to_host()
    cuda.synchronize()
    output_copy_back_wall_sec = time.perf_counter() - copy_back_start

    validation = _run_reference_validation(
        prepared=prepared,
        force_x=force_x,
        force_y=force_y,
        theta=theta,
        validate=validate,
        validate_max_body_count=validate_max_body_count,
    )
    if not bool(validation["skipped"]) and not bool(validation["passed"]):
        raise AssertionError("Numba CUDA fused subtree output failed CPU validation")

    kernel_event_seconds = [float(row["kernel_event_ms"]) / 1000.0 for row in repeat_rows]
    kernel_wall_seconds = [float(row["kernel_wall_sec"]) for row in repeat_rows]
    event_median_sec = _median(kernel_event_seconds)
    cpu_baseline = M45_CPU_FUSED_SECONDS.get(int(body_count))
    optix_scale_baseline = M41_PREPARED_OPTIX_NUMBA_SECONDS.get(int(body_count))
    optix_app_baseline = M42_APP_MODE_OPTIX_NUMBA_SECONDS.get(int(body_count))

    comparisons: dict[str, Any] = {
        "m45_cpu_fused_hot_sec": cpu_baseline,
        "m41_prepared_optix_numba_hot_sec": optix_scale_baseline,
        "m42_app_mode_optix_numba_hot_sec": optix_app_baseline,
    }
    if cpu_baseline is not None and event_median_sec > 0.0:
        comparisons["m52_event_sec_over_m45_cpu_fused"] = event_median_sec / cpu_baseline
    if optix_scale_baseline is not None and event_median_sec > 0.0:
        comparisons["m41_optix_numba_over_m52_event_sec"] = optix_scale_baseline / event_median_sec
    if optix_app_baseline is not None and event_median_sec > 0.0:
        comparisons["m42_app_optix_numba_over_m52_event_sec"] = optix_app_baseline / event_median_sec

    tree = prepared["tree"]
    return {
        "goal": GOAL,
        "version": VERSION,
        "app": "barnes_hut_force_app",
        "backend": "numba_cuda_partner_prototype",
        "mode": MODE,
        "body_count": int(body_count),
        "theta": float(theta),
        "softening": float(softening),
        "bucket_size": int(bucket_size),
        "max_depth": int(max_depth),
        "threads": int(threads),
        "blocks": int(blocks),
        "source_count": int(source_count),
        "node_count": int(node_count),
        "member_count": int(member_count),
        "child_edge_count": int(child_edge_count),
        "tree_summary": tree["summary"],
        "run_phases": {
            "tree_prepare_wall_sec": tree_prepare_wall_sec,
            "host_to_device_wall_sec": float(transfer_phases["host_to_device_wall_sec"]),
            "compile_and_first_launch_wall_sec": compile_and_first_launch_wall_sec,
            "output_copy_back_wall_sec": output_copy_back_wall_sec,
            "total_wall_sec": time.perf_counter() - run_start,
            "warmup": int(warmup),
            "repeat": int(repeats),
            "kernel_event_median_sec": event_median_sec,
            "kernel_wall_median_sec": _median(kernel_wall_seconds),
        },
        "repeat_rows": repeat_rows,
        "vector_sum_summary": {
            "checksum_force_x": float(force_x.sum()),
            "checksum_force_y": float(force_y.sum()),
            "aggregate_contribution_count": int(aggregate.sum()),
            "exact_contribution_count": int(exact.sum()),
            "contribution_row_count": int(aggregate.sum() + exact.sum()),
            "visited_node_count": int(visited.sum()),
            "repeat": int(repeats),
            "warmup": int(warmup),
        },
        "validation": validation,
        "comparison_baselines": comparisons,
        "numba_cuda_toolchain_environment": env,
        "claim_flags": {
            "numba_cuda_python_source_used": True,
            "cxx_cuda_extension_used": False,
            "torch_extension_used": False,
            "rt_cores_used": False,
            "rtdl_native_optix_primitive_used_for_hot_kernel": False,
            "frontier_rows_materialized_on_host": False,
            "contribution_rows_materialized_on_host": False,
            "final_vector_rows_copied_to_host_for_evidence": True,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "app_specific_native_engine_logic_used": False,
        },
        "boundary": (
            "M52 is a Python-source Numba CUDA fused-subtree partner prototype. "
            "It measures whether a no-C++ fused CUDA partner can remove the "
            "frontier-materialization bottleneck seen in Barnes-Hut. It is not "
            "an RT-core primitive, not an OptiX/Embree comparison row, and not "
            "public speedup wording."
        ),
    }


def dry_run_payload(*, body_counts: tuple[int, ...], bucket_size: int, max_depth: int) -> dict[str, Any]:
    return {
        "goal": GOAL,
        "version": VERSION,
        "mode": MODE,
        "body_counts": tuple(int(value) for value in body_counts),
        "bucket_size": int(bucket_size),
        "max_depth": int(max_depth),
        "dry_run": True,
        "planned_claim_flags": {
            "numba_cuda_python_source_used": True,
            "cxx_cuda_extension_used": False,
            "torch_extension_used": False,
            "rt_cores_used": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
        },
        "planned_output": (
            "one JSON row per body count with CUDA event hot timing, wall timing, "
            "validation metadata, vector checksum, and M41/M42/M45 diagnostic ratios"
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=GOAL)
    parser.add_argument("--body-counts", default="8192,16384,32768")
    parser.add_argument("--bucket-size", type=int, default=64)
    parser.add_argument("--max-depth", type=int, default=COMPARISON_MAX_DEPTH)
    parser.add_argument("--theta", type=float, default=COMPARISON_THETA)
    parser.add_argument("--softening", type=float, default=app.SOFTENING)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--repeat", type=int, default=11)
    parser.add_argument("--threads", type=int, default=128)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--validate-max-body-count", type=int, default=512)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", default="")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    body_counts = _parse_body_counts(args.body_counts)
    if args.dry_run:
        payload: dict[str, Any] = dry_run_payload(
            body_counts=body_counts,
            bucket_size=args.bucket_size,
            max_depth=args.max_depth,
        )
    else:
        configure_numba_cuda_toolchain_environment()
        rows = [
            run_numba_cuda_fused_subtree(
                body_count=body_count,
                bucket_size=args.bucket_size,
                max_depth=args.max_depth,
                theta=args.theta,
                softening=args.softening,
                warmup=args.warmup,
                repeats=args.repeat,
                threads=args.threads,
                validate=args.validate,
                validate_max_body_count=args.validate_max_body_count,
            )
            for body_count in body_counts
        ]
        payload = {
            "goal": GOAL,
            "version": VERSION,
            "mode": MODE,
            "rows": rows,
            "summary": {
                "body_counts": [int(row["body_count"]) for row in rows],
                "repeat": int(args.repeat),
                "warmup": int(args.warmup),
                "best_event_median_sec": min(
                    float(row["run_phases"]["kernel_event_median_sec"]) for row in rows
                ),
                "claim_boundary": (
                    "prototype CUDA-core partner evidence only; no RT-core or public "
                    "backend speedup claim is authorized"
                ),
            },
        }

    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
