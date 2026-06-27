#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any


VERSION = "rtdl.v4.goal4676.aggregate_frontier_focused_pod_benchmark.v1"
ROOT = Path(__file__).resolve().parents[1]
APP_MODULE = "examples.current.research_benchmarks.barnes_hut.rtdl_barnes_hut_benchmark_app"
_CURRENT_BARNES_HELPER_MODULE = None


def _python(_root: Path) -> str:
    return os.environ.get("RTDL_GOAL4676_PYTHON", "/root/rtdl_v4_venv/bin/python")


def _cuda_prefix() -> Path:
    return Path(
        os.environ.get(
            "RTDL_GOAL4676_CUDA_PREFIX",
            "/root/rtdl_v4_venv/lib/python3.12/site-packages/nvidia/cuda_nvcc",
        )
    )


def _versions() -> dict[str, dict[str, Any]]:
    return {
        "v2_14": {
            "root": Path(os.environ.get("RTDL_GOAL4676_V2_ROOT", "/root/rtdl_v2_14_tag")),
            "route": "v2_14_optix_host_frontier_numba_cpu_continuation",
            "tag_native_optix_build": False,
        },
        "v3_0_2": {
            "root": Path(os.environ.get("RTDL_GOAL4676_V3_ROOT", "/root/rtdl_v3_0_2_tag")),
            "route": "v3_0_2_device_columns_explicit_partner_continuation",
            "tag_native_optix_build": False,
        },
        "v4_current": {
            "root": Path(os.environ.get("RTDL_GOAL4676_V4_ROOT", "/root/rtdl_v4_candidate_pod")),
            "route": "v4_candidate_runner_explicit_partner_continuation",
            "tag_native_optix_build": True,
        },
    }


def _profile_values(profile: str) -> dict[str, Any]:
    if profile == "smoke":
        return {
            "body_count": 2048,
            "repeat": 1,
            "warmup": 0,
            "correctness_body_count": 1024,
            "frontier_capacity_multiplier": 700,
            "timeout_sec": 600,
        }
    if profile == "serious":
        return {
            "body_count": 32768,
            "repeat": 7,
            "warmup": 2,
            "correctness_body_count": 2048,
            "frontier_capacity_multiplier": 700,
            "timeout_sec": 3600,
        }
    if profile == "large":
        return {
            "body_count": 131072,
            "repeat": 11,
            "warmup": 2,
            "correctness_body_count": 2048,
            "frontier_capacity_multiplier": 700,
            "timeout_sec": 7200,
        }
    raise ValueError(f"unknown profile {profile!r}")


def _env_for(root: Path, *, tag_native_optix_build: bool) -> dict[str, str]:
    env = os.environ.copy()
    cuda_prefix = _cuda_prefix()
    env["PYTHONPATH"] = f"{root / 'src'}:{ROOT}"
    env["CUDA_HOME"] = str(cuda_prefix)
    env["CUDA_PATH"] = str(cuda_prefix)
    env["NUMBA_CUDA_PREFIX"] = str(cuda_prefix)
    env["NUMBA_CUDA_NVVM"] = str(cuda_prefix / "nvvm" / "lib64" / "libnvvm.so")
    env["LD_LIBRARY_PATH"] = f"{cuda_prefix / 'nvvm' / 'lib64'}:{env.get('LD_LIBRARY_PATH', '')}"
    optix = root / "build" / ("librtdl_optix.so" if tag_native_optix_build else "librtdl_optix.v4compat.so")
    embree = root / "build" / "librtdl_embree.so"
    env["RTDL_OPTIX_LIBRARY"] = str(optix)
    env["RTDL_OPTIX_LIB"] = str(optix)
    env["RTDL_EMBREE_LIBRARY"] = str(embree)
    env["RTDL_EMBREE_LIB"] = str(embree)
    return env


def _copy_compat_libraries(versions: dict[str, dict[str, Any]]) -> None:
    v4_optix = versions["v4_current"]["root"] / "build" / "librtdl_optix.so"
    if not v4_optix.exists():
        return
    for name in ("v2_14", "v3_0_2"):
        root = versions[name]["root"]
        target = root / "build" / "librtdl_optix.v4compat.so"
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists() or target.stat().st_size != v4_optix.stat().st_size:
            target.write_bytes(v4_optix.read_bytes())


def _median(rows: list[dict[str, float]], field: str) -> float:
    return float(statistics.median(float(row[field]) for row in rows))


def _device_column_to_list(column: object, *, value_type: type) -> list[object]:
    if hasattr(column, "copy_to_host"):
        values = column.copy_to_host()
    elif hasattr(column, "get"):
        values = column.get()
    else:
        values = column
    if hasattr(values, "tolist"):
        values = values.tolist()
    return [value_type(value) for value in values]


def _force_rows_from_device_columns(columns: dict[str, object]) -> tuple[dict[str, object], ...]:
    source_ids = _device_column_to_list(columns["source_ids"], value_type=int)
    vector_x = _device_column_to_list(columns["vector_x"], value_type=float)
    vector_y = _device_column_to_list(columns["vector_y"], value_type=float)
    return tuple(
        {"body_id": int(source_id), "force_x": float(force_x), "force_y": float(force_y)}
        for source_id, force_x, force_y in zip(source_ids, vector_x, vector_y)
    )


def _validate_force_rows(
    rt: Any,
    bh: Any,
    bodies: tuple[object, ...],
    tree_nodes: tuple[object, ...],
    force_rows: tuple[dict[str, object], ...],
    *,
    theta: float,
    skip_validation: bool,
) -> dict[str, object]:
    if skip_validation or len(bodies) > 2048:
        return {
            "skipped": True,
            "reason": "user_skip_validation" if skip_validation else "body_count_above_2048",
        }
    reference = rt.sum_aggregate_frontier_weighted_vectors_2d(
        bodies,
        bodies,
        tree_nodes,
        theta=theta,
        softening=bh.app.SOFTENING,
    )
    expected_by_id = {
        int(row["source_id"]): (float(row["vector_x"]), float(row["vector_y"]))
        for row in reference["vector_sum_rows"]
    }
    max_abs_diff_x = max(
        abs(float(row["force_x"]) - expected_by_id[int(row["body_id"])][0])
        for row in force_rows
    )
    max_abs_diff_y = max(
        abs(float(row["force_y"]) - expected_by_id[int(row["body_id"])][1])
        for row in force_rows
    )
    passed = max_abs_diff_x <= 1.0e-7 and max_abs_diff_y <= 1.0e-7
    if not passed:
        raise AssertionError("aggregate-frontier focused route failed CPU reference validation")
    return {
        "skipped": False,
        "compared_against": "sum_aggregate_frontier_weighted_vectors_2d_cpu_reference",
        "tolerance": 1.0e-7,
        "max_abs_diff_x": max_abs_diff_x,
        "max_abs_diff_y": max_abs_diff_y,
        "passed": passed,
        "reference_frontier_row_count": int(reference["summary"]["contribution_row_count"]),
    }


def _host_python_weighted_vector_sum_from_frontier_i64_rows(
    bodies: tuple[object, ...],
    tree_nodes: tuple[object, ...],
    collection: dict[str, object],
    *,
    softening: float,
) -> tuple[tuple[dict[str, object], ...], dict[str, object]]:
    source_by_id = {int(getattr(body, "id")): body for body in bodies}
    target_by_id = dict(source_by_id)
    node_by_id = {int(getattr(node, "id")): node for node in tree_nodes}
    vector_x_by_id = {source_id: 0.0 for source_id in source_by_id}
    vector_y_by_id = {source_id: 0.0 for source_id in source_by_id}
    aggregate_count_by_id = {source_id: 0 for source_id in source_by_id}
    exact_count_by_id = {source_id: 0 for source_id in source_by_id}
    softening_sq = float(softening) * float(softening)
    aggregate_count = 0
    exact_count = 0
    frontier_rows = tuple(collection["frontier_i64_rows"])

    for raw_row in frontier_rows:
        source_id = int(raw_row[0])
        kind_code = int(raw_row[1])
        item_id = int(raw_row[2])
        source = source_by_id[source_id]
        if kind_code == 1:
            target = node_by_id[item_id]
            target_x = float(getattr(target, "cx"))
            target_y = float(getattr(target, "cy"))
            target_mass = float(getattr(target, "mass"))
            aggregate_count += 1
            aggregate_count_by_id[source_id] += 1
        elif kind_code == 2:
            target_body = target_by_id[item_id]
            target_x = float(getattr(target_body, "x"))
            target_y = float(getattr(target_body, "y"))
            target_mass = float(getattr(target_body, "mass"))
            exact_count += 1
            exact_count_by_id[source_id] += 1
        else:
            continue

        dx = target_x - float(getattr(source, "x"))
        dy = target_y - float(getattr(source, "y"))
        dist_sq = dx * dx + dy * dy + softening_sq
        if dist_sq == 0.0:
            continue
        inv_dist = 1.0 / (dist_sq ** 0.5)
        scale = float(getattr(source, "mass")) * target_mass * inv_dist * inv_dist * inv_dist
        vector_x_by_id[source_id] += dx * scale
        vector_y_by_id[source_id] += dy * scale

    force_rows = tuple(
        {
            "body_id": int(source_id),
            "force_x": float(vector_x_by_id[source_id]),
            "force_y": float(vector_y_by_id[source_id]),
            "contribution_count": int(aggregate_count_by_id[source_id] + exact_count_by_id[source_id]),
            "aggregate_contribution_count": int(aggregate_count_by_id[source_id]),
            "exact_contribution_count": int(exact_count_by_id[source_id]),
        }
        for source_id in sorted(source_by_id)
    )
    return force_rows, {
        "frontier_row_count": len(frontier_rows),
        "aggregate_contribution_row_count": aggregate_count,
        "exact_contribution_row_count": exact_count,
        "source_count": len(source_by_id),
        "softening": float(softening),
        "contribution_rows_materialized_on_host": False,
        "frontier_i64_rows_materialized_on_host": True,
        "streamed_host_accumulation": True,
        "python_host_fallback_used": True,
        "numba_cpu_njit_used": False,
    }


def _load_current_barnes_hut_helper(name: str) -> object | None:
    global _CURRENT_BARNES_HELPER_MODULE
    if _CURRENT_BARNES_HELPER_MODULE is None:
        path = ROOT / "examples" / "current" / "research_benchmarks" / "barnes_hut" / "rtdl_barnes_hut_benchmark_app.py"
        spec = importlib.util.spec_from_file_location("_rtdl_current_barnes_hut_helper", path)
        if spec is None or spec.loader is None:
            return None
        old_path = list(sys.path)
        try:
            sys.path.insert(0, str(ROOT / "src"))
            sys.path.insert(0, str(ROOT))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            _CURRENT_BARNES_HELPER_MODULE = module
        finally:
            sys.path[:] = old_path
    return getattr(_CURRENT_BARNES_HELPER_MODULE, name, None)


def _import_worker_modules() -> tuple[Any, Any]:
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))
    import importlib

    import rtdsl as rt

    bh = importlib.import_module(APP_MODULE)
    return rt, bh


def _make_problem(rt: Any, bh: Any, *, body_count: int, bucket_size: int, max_depth: int) -> tuple[Any, Any, Any]:
    bodies = tuple(bh._make_bodies(body_count))
    tree = rt.build_bucketized_aggregate_tree_2d(
        bodies,
        bucket_size=bucket_size,
        max_depth=max_depth,
    )
    return bodies, tree, tuple(tree["nodes"])


def _run_v2_14_optix_host_numba(args: argparse.Namespace) -> dict[str, object]:
    rt, bh = _import_worker_modules()
    collect = getattr(rt, "collect_aggregate_frontier_2d_optix", None)
    if collect is None:
        raise RuntimeError(
            "V2.14 denominator requires collect_aggregate_frontier_2d_optix; "
            "do not silently fall back to CPU-only"
        )
    bodies, tree, tree_nodes = _make_problem(
        rt,
        bh,
        body_count=args.body_count,
        bucket_size=args.bucket_size,
        max_depth=args.max_depth,
    )
    capacity = max(1024, int(args.body_count) * int(args.frontier_capacity_multiplier))
    repeats: list[dict[str, float]] = []
    last_force_rows: tuple[dict[str, object], ...] | None = None
    last_collection: dict[str, object] | None = None

    for repeat_index in range(int(args.warmup) + int(args.repeat)):
        collect_start = time.perf_counter()
        collection = collect(
            bodies,
            tree_nodes,
            theta=args.theta,
            max_total_rows=capacity,
        )
        frontier_collect_seconds = time.perf_counter() - collect_start
        vector_start = time.perf_counter()
        host_numba_helper = getattr(
            bh,
            "_host_numba_cpu_weighted_vector_sum_from_frontier_i64_rows",
            None,
        )
        if host_numba_helper is None:
            host_numba_helper = _load_current_barnes_hut_helper(
                "_host_numba_cpu_weighted_vector_sum_from_frontier_i64_rows"
            )
        if host_numba_helper is not None:
            force_rows, vector_summary = host_numba_helper(
                bodies,
                tree_nodes,
                collection,
                softening=bh.app.SOFTENING,
                query_repeat=1,
                warmup=0,
            )
        else:
            host_helper = getattr(bh, "_host_weighted_vector_sum_from_frontier_rows", None)
            if host_helper is None:
                force_rows, vector_summary = _host_python_weighted_vector_sum_from_frontier_i64_rows(
                    bodies,
                    tree_nodes,
                    collection,
                    softening=bh.app.SOFTENING,
                )
            else:
                force_rows, vector_summary = host_helper(
                    bodies,
                    tree_nodes,
                    tuple(collection["frontier_rows"]),
                    softening=bh.app.SOFTENING,
                )
            vector_summary = {
                **vector_summary,
                "v2_14_missing_host_numba_helper_fallback": True,
                "fallback_contract": "same_frontier_rows_host_weighted_vector_sum",
            }
        vector_wall_seconds = time.perf_counter() - vector_start
        if repeat_index >= int(args.warmup):
            repeats.append(
                {
                    "repeat_index": float(repeat_index - int(args.warmup)),
                    "frontier_collect_seconds": float(frontier_collect_seconds),
                    "host_numba_vector_wall_seconds": float(vector_wall_seconds),
                    "hot_seconds": float(frontier_collect_seconds + vector_wall_seconds),
                    "wall_seconds": float(frontier_collect_seconds + vector_wall_seconds),
                    "frontier_row_count": float(collection["summary"]["frontier_row_count"]),
                    "aggregate_contribution_row_count": float(
                        collection["summary"]["accepted_aggregate_row_count"]
                    ),
                    "exact_contribution_row_count": float(collection["summary"]["fallback_exact_row_count"]),
                }
            )
            last_force_rows = tuple(force_rows)
            last_collection = collection

    if last_force_rows is None or last_collection is None:
        raise RuntimeError("no V2.14 hot repeat executed")
    validation = _validate_force_rows(
        rt,
        bh,
        bodies,
        tree_nodes,
        last_force_rows,
        theta=args.theta,
        skip_validation=args.skip_validation,
    )
    return {
        "schema": VERSION,
        "version": "v2_14",
        "route": "v2_14_optix_host_frontier_numba_cpu_continuation",
        "app": "barnes_hut_force_app",
        "body_count": int(args.body_count),
        "theta": float(args.theta),
        "partner": "numba_cpu",
        "tree_summary": tree["summary"],
        "capacity": {"frontier_row_capacity": int(capacity)},
        "hot_repeats": repeats,
        "medians": {
            "frontier_collect_seconds": _median(repeats, "frontier_collect_seconds"),
            "host_numba_vector_wall_seconds": _median(repeats, "host_numba_vector_wall_seconds"),
            "hot_seconds": _median(repeats, "hot_seconds"),
            "wall_seconds": _median(repeats, "wall_seconds"),
        },
        "frontier_summary": {
            "contract": last_collection["metadata"]["contract"],
            "native_symbol": last_collection["metadata"].get("native_symbol"),
            "frontier_row_count": int(last_collection["summary"]["frontier_row_count"]),
            "frontier_rows_materialized_on_host": True,
        },
        "validation": validation,
        "checksum": {
            "force_x": sum(float(row["force_x"]) for row in last_force_rows),
            "force_y": sum(float(row["force_y"]) for row in last_force_rows),
        },
        "claim_flags": {
            "same_logical_frontier_contract": True,
            "device_column_contract": False,
            "frontier_rows_materialized_on_host": True,
            "host_frontier_materialization_in_hot_path": True,
            "partner_migration_counts_as_speed": False,
        },
    }


def _run_device_columns_partner(args: argparse.Namespace, *, use_v4_runner: bool) -> dict[str, object]:
    rt, bh = _import_worker_modules()
    bodies, tree, tree_nodes = _make_problem(
        rt,
        bh,
        body_count=args.body_count,
        bucket_size=args.bucket_size,
        max_depth=args.max_depth,
    )
    if args.partner == "numba":
        prepared_vector = rt.prepare_aggregate_frontier_device_columns_weighted_vectors_2d_numba(
            bodies,
            bodies,
            tree_nodes,
        )
        partner_contract = rt.AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_NUMBA_CONTRACT
    else:
        prepared_vector = rt.prepare_aggregate_frontier_device_columns_weighted_vectors_2d_cupy(
            bodies,
            bodies,
            tree_nodes,
        )
        partner_contract = rt.AGGREGATE_FRONTIER_DEVICE_COLUMNS_PREPARED_WEIGHTED_VECTOR_SUM_2D_CONTRACT

    if use_v4_runner:
        import rtdsl.v4 as rtdl_v4

        prepared_frontier = rtdl_v4.prepare_aggregate_frontier_device_columns_2d_prepared_runner_v4(
            tree_nodes,
            theta=args.theta,
            downstream_partner=args.partner,
        )
        route = "v4_candidate_runner_explicit_partner_continuation"
        version = "v4_current"
    else:
        prepared_frontier = rt.prepare_aggregate_frontier_device_columns_2d_optix(
            tree_nodes,
            theta=args.theta,
        )
        route = "v3_0_2_device_columns_explicit_partner_continuation"
        version = "v3_0_2"

    initial_capacity = max(1024, int(args.body_count) * int(args.frontier_capacity_multiplier))
    repeats: list[dict[str, float]] = []
    capacity_attempts: list[dict[str, object]] = []
    last_force_rows: tuple[dict[str, object], ...] | None = None
    last_frontier: object | None = None
    last_vector_sum: dict[str, object] | None = None
    last_runner_metadata: dict[str, object] = {}

    def run_frontier(capacity: int) -> tuple[object, dict[str, object]]:
        if use_v4_runner:
            result = prepared_frontier.run_device_columns(
                row_capacity=capacity,
                **prepared_vector.frontier_source_device_args(),
            )
            return result["frontier"], dict(result.get("metadata", {}))
        return prepared_frontier.run_device_columns(
            row_capacity=capacity,
            **prepared_vector.frontier_source_device_args(),
        ), {}

    with prepared_frontier:
        capacity = initial_capacity
        for attempt_index in range(4):
            frontier, runner_metadata = run_frontier(capacity)
            attempt = {
                "attempt_index": attempt_index,
                "capacity": int(capacity),
                "overflow": bool(getattr(frontier, "overflow", False)),
                "row_count": int(getattr(frontier, "row_count", 0)),
                "attempted_count": int(getattr(frontier, "attempted_count", 0)),
                "traversal_seconds": float(getattr(frontier, "traversal_seconds", 0.0)),
            }
            capacity_attempts.append(attempt)
            if not bool(getattr(frontier, "overflow", False)):
                capacity = int(getattr(frontier, "attempted_count", capacity)) + 1024
                last_runner_metadata = runner_metadata
                break
            capacity = int(getattr(frontier, "attempted_count", capacity)) + 1024
        else:
            raise RuntimeError("aggregate-frontier device-column capacity probe overflowed four times")

        for _ in range(int(args.warmup)):
            frontier, _runner_metadata = run_frontier(capacity)
            if bool(getattr(frontier, "overflow", False)):
                raise RuntimeError("warmup overflowed after capacity probe")
            prepared_vector.sum(frontier, softening=bh.app.SOFTENING)

        for repeat_index in range(int(args.repeat)):
            wall_start = time.perf_counter()
            frontier, runner_metadata = run_frontier(capacity)
            if bool(getattr(frontier, "overflow", False)):
                raise RuntimeError("hot repeat overflowed after capacity probe")
            vector_sum = prepared_vector.sum(frontier, softening=bh.app.SOFTENING)
            wall_seconds = time.perf_counter() - wall_start
            vector_metadata = vector_sum["metadata"]
            frontier_seconds = float(getattr(frontier, "traversal_seconds", 0.0))
            partner_seconds = float(vector_metadata["partner_seconds"])
            repeats.append(
                {
                    "repeat_index": float(repeat_index),
                    "frontier_traversal_seconds": frontier_seconds,
                    "partner_seconds": partner_seconds,
                    "hot_seconds": frontier_seconds + partner_seconds,
                    "wall_seconds": float(wall_seconds),
                    "frontier_row_count": float(vector_metadata["frontier_row_count"]),
                    "aggregate_contribution_row_count": float(
                        vector_metadata["aggregate_contribution_row_count"]
                    ),
                    "exact_contribution_row_count": float(vector_metadata["exact_contribution_row_count"]),
                }
            )
            last_frontier = frontier
            last_vector_sum = vector_sum
            last_runner_metadata = runner_metadata

    if last_frontier is None or last_vector_sum is None:
        raise RuntimeError("no device-column hot repeat executed")
    force_rows = _force_rows_from_device_columns(last_vector_sum["columns"])
    validation = _validate_force_rows(
        rt,
        bh,
        bodies,
        tree_nodes,
        force_rows,
        theta=args.theta,
        skip_validation=args.skip_validation,
    )
    frontier_host_materialized = bool(
        last_runner_metadata.get(
            "frontier_columns_materialized_on_host",
            getattr(last_frontier, "frontier_columns_materialized_on_host", False),
        )
    )
    row_offsets_host_materialized = bool(
        last_runner_metadata.get(
            "row_offsets_materialized_on_host",
            getattr(last_frontier, "row_offsets_materialized_on_host", False),
        )
    )
    return {
        "schema": VERSION,
        "version": version,
        "route": route,
        "app": "barnes_hut_force_app",
        "body_count": int(args.body_count),
        "theta": float(args.theta),
        "partner": args.partner,
        "tree_summary": tree["summary"],
        "capacity": {
            "initial_capacity": int(initial_capacity),
            "final_row_capacity": int(capacity),
            "capacity_attempts": capacity_attempts,
        },
        "hot_repeats": repeats,
        "medians": {
            "frontier_traversal_seconds": _median(repeats, "frontier_traversal_seconds"),
            "partner_seconds": _median(repeats, "partner_seconds"),
            "hot_seconds": _median(repeats, "hot_seconds"),
            "wall_seconds": _median(repeats, "wall_seconds"),
        },
        "frontier_summary": {
            "contract": rt.AGGREGATE_FRONTIER_DEVICE_COLUMNS_2D_CONTRACT,
            "partner_contract": partner_contract,
            "frontier_row_count": int(getattr(last_frontier, "row_count", 0)),
            "frontier_columns_materialized_on_host": frontier_host_materialized,
            "row_offsets_materialized_on_host": row_offsets_host_materialized,
            "runner_metadata": last_runner_metadata,
        },
        "validation": validation,
        "checksum": {
            "force_x": sum(float(row["force_x"]) for row in force_rows),
            "force_y": sum(float(row["force_y"]) for row in force_rows),
        },
        "claim_flags": {
            "same_logical_frontier_contract": True,
            "device_column_contract": True,
            "frontier_columns_materialized_on_host": frontier_host_materialized,
            "row_offsets_materialized_on_host": row_offsets_host_materialized,
            "host_frontier_materialization_in_hot_path": (
                frontier_host_materialized or row_offsets_host_materialized
            ),
            "automatic_partner_selection_allowed": False,
            "partner_migration_counts_as_speed": False,
        },
    }


def _run_worker(args: argparse.Namespace) -> int:
    if args.route == "v2_14_optix_host_frontier_numba_cpu_continuation":
        payload = _run_v2_14_optix_host_numba(args)
    elif args.route == "v3_0_2_device_columns_explicit_partner_continuation":
        payload = _run_device_columns_partner(args, use_v4_runner=False)
    elif args.route == "v4_candidate_runner_explicit_partner_continuation":
        payload = _run_device_columns_partner(args, use_v4_runner=True)
    else:
        raise ValueError(f"unsupported worker route {args.route!r}")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _run_command(
    *,
    version: str,
    run_kind: str,
    command: list[str],
    cwd: Path,
    env: dict[str, str],
    out_dir: Path,
    timeout_sec: int,
) -> dict[str, Any]:
    stem = f"{version}_{run_kind}"
    stdout_path = out_dir / f"{stem}.json"
    stderr_path = out_dir / f"{stem}.stderr.txt"
    started = time.time()
    started_perf = time.perf_counter()
    print(f"[goal4676] BEGIN {stem}", flush=True)
    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        try:
            completed = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                text=True,
                stdout=stdout,
                stderr=stderr,
                timeout=timeout_sec,
                check=False,
            )
            rc = int(completed.returncode)
            timed_out = False
            error = None
        except subprocess.TimeoutExpired as exc:
            rc = 124
            timed_out = True
            error = f"timeout after {exc.timeout} seconds"
    elapsed = time.perf_counter() - started_perf
    print(f"[goal4676] END {stem} rc={rc} elapsed={elapsed:.3f}s", flush=True)
    return {
        "version": version,
        "run_kind": run_kind,
        "command": command,
        "cwd": str(cwd),
        "stdout_json": str(stdout_path),
        "stderr": str(stderr_path),
        "returncode": rc,
        "timed_out": timed_out,
        "error": error,
        "runner_elapsed_sec": elapsed,
        "started_unix": started,
        "ended_unix": time.time(),
    }


def _read_payload(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _ratio(denominator: float | None, numerator: float | None) -> float | None:
    if denominator is None or numerator is None or numerator <= 0.0:
        return None
    return float(denominator) / float(numerator)


def _metric(payload: dict[str, Any] | None, field: str) -> float | None:
    if not payload:
        return None
    value = payload.get("medians", {}).get(field)
    return float(value) if isinstance(value, (int, float)) else None


def _checksum_close(a: dict[str, Any] | None, b: dict[str, Any] | None) -> bool:
    if not a or not b:
        return False
    ca = a.get("checksum", {})
    cb = b.get("checksum", {})
    for field in ("force_x", "force_y"):
        av = ca.get(field)
        bv = cb.get(field)
        if not isinstance(av, (int, float)) or not isinstance(bv, (int, float)):
            return False
        if not math.isclose(float(av), float(bv), rel_tol=1.0e-6, abs_tol=1.0e-5):
            return False
    return True


def _validation_ok(payload: dict[str, Any] | None) -> bool:
    if not payload:
        return False
    validation = payload.get("validation")
    if not isinstance(validation, dict):
        return False
    if validation.get("skipped") is True:
        return True
    return validation.get("passed") is True


def _host_materialization(payload: dict[str, Any] | None) -> bool | None:
    if not payload:
        return None
    flags = payload.get("claim_flags")
    if not isinstance(flags, dict):
        return None
    value = flags.get("host_frontier_materialization_in_hot_path")
    return bool(value) if isinstance(value, bool) else None


def _analyze(executions: list[dict[str, Any]], profile: str, partner: str) -> dict[str, Any]:
    payloads: dict[tuple[str, str], dict[str, Any] | None] = {}
    for execution in executions:
        payloads[(execution["version"], execution["run_kind"])] = _read_payload(Path(execution["stdout_json"]))

    serious_v2 = payloads.get(("v2_14", "serious"))
    serious_v3 = payloads.get(("v3_0_2", "serious"))
    serious_v4 = payloads.get(("v4_current", "serious"))
    correct_v2 = payloads.get(("v2_14", "correctness"))
    correct_v3 = payloads.get(("v3_0_2", "correctness"))
    correct_v4 = payloads.get(("v4_current", "correctness"))

    v2_frontier = _metric(serious_v2, "frontier_collect_seconds")
    v2_hot = _metric(serious_v2, "hot_seconds")
    v2_wall = _metric(serious_v2, "wall_seconds")
    v4_frontier = _metric(serious_v4, "frontier_traversal_seconds")
    v4_hot = _metric(serious_v4, "hot_seconds")
    v4_wall = _metric(serious_v4, "wall_seconds")
    ratios = {
        "v4_frontier_only_hot_over_v2_14": _ratio(v2_frontier, v4_frontier),
        "v4_full_hot_over_v2_14": _ratio(v2_hot, v4_hot),
        "v4_full_wall_over_v2_14": _ratio(v2_wall, v4_wall),
        "v4_full_hot_over_v3_0_2_control": _ratio(_metric(serious_v3, "hot_seconds"), v4_hot),
    }
    correctness_companion_ok = all(_validation_ok(item) for item in (correct_v2, correct_v3, correct_v4))
    checksum_parity = _checksum_close(serious_v2, serious_v4) and _checksum_close(serious_v3, serious_v4)
    no_v4_host_materialization = _host_materialization(serious_v4) is False
    all_returncodes_ok = all(int(item["returncode"]) == 0 for item in executions)
    pass_fail = {
        "all_subprocesses_returned_zero": all_returncodes_ok,
        "correctness_companion_ok": correctness_companion_ok,
        "large_run_checksum_parity": checksum_parity,
        "v4_host_frontier_materialization_in_hot_path": _host_materialization(serious_v4),
        "v4_frontier_only_hot_bar_pass": (
            ratios["v4_frontier_only_hot_over_v2_14"] is not None
            and ratios["v4_frontier_only_hot_over_v2_14"] >= 1.20
        ),
        "v4_full_hot_bar_pass": (
            ratios["v4_full_hot_over_v2_14"] is not None
            and ratios["v4_full_hot_over_v2_14"] >= 1.20
        ),
        "v4_full_wall_bar_pass": (
            ratios["v4_full_wall_over_v2_14"] is not None
            and ratios["v4_full_wall_over_v2_14"] >= 1.10
        ),
        "partner_migration_counted_as_speed": False,
    }
    pass_fail["goal4676_pass"] = all(
        bool(pass_fail[key])
        for key in (
            "all_subprocesses_returned_zero",
            "correctness_companion_ok",
            "large_run_checksum_parity",
            "v4_frontier_only_hot_bar_pass",
            "v4_full_hot_bar_pass",
            "v4_full_wall_bar_pass",
        )
    ) and no_v4_host_materialization
    return {
        "schema": VERSION,
        "profile": profile,
        "partner": partner,
        "executions": executions,
        "ratios": ratios,
        "pass_fail": pass_fail,
        "decision_label": (
            "goal4676_pass_true_v4_aggregate_frontier_candidate"
            if pass_fail["goal4676_pass"]
            else "goal4676_fail_or_inconclusive_do_not_promote"
        ),
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_wording_authorized": False,
            "whole_app_high_performance_wording_authorized": False,
            "rt_core_speedup_wording_authorized": False,
            "true_zero_copy_wording_authorized": False,
        },
    }


def _print_plan(profile: str, partner: str) -> dict[str, Any]:
    values = _profile_values(profile)
    return {
        "schema": VERSION,
        "mode": "plan",
        "profile": profile,
        "partner": partner,
        "values": values,
        "versions": {
            name: {"root": str(row["root"]), "route": row["route"]}
            for name, row in _versions().items()
        },
        "bars": {
            "v4_frontier_only_hot_over_v2_14_min": 1.20,
            "v4_full_hot_over_v2_14_min": 1.20,
            "v4_full_wall_over_v2_14_min": 1.10,
            "partner_migration_counts_as_speed": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run V4 Goal4676 aggregate-frontier focused POD benchmark.")
    parser.add_argument("--profile", choices=("smoke", "serious", "large"), default="serious")
    parser.add_argument("--partner", choices=("cupy", "numba"), default="cupy")
    parser.add_argument("--out-dir", type=Path)
    parser.add_argument("--print-plan", action="store_true")
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--route")
    parser.add_argument("--body-count", type=int)
    parser.add_argument("--theta", type=float, default=0.5)
    parser.add_argument("--bucket-size", type=int, default=32)
    parser.add_argument("--max-depth", type=int, default=32)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--warmup", type=int, default=0)
    parser.add_argument("--frontier-capacity-multiplier", type=int, default=700)
    parser.add_argument("--skip-validation", action="store_true")
    args = parser.parse_args()

    if args.print_plan:
        print(json.dumps(_print_plan(args.profile, args.partner), indent=2, sort_keys=True))
        return 0
    if args.worker:
        return _run_worker(args)

    values = _profile_values(args.profile)
    versions = _versions()
    _copy_compat_libraries(versions)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    out_dir = args.out_dir or ROOT / "future" / "v4" / "evidence" / f"v4_goal4676_aggregate_frontier_pod_{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    executions: list[dict[str, Any]] = []
    for run_kind, body_count, skip_validation in (
        ("serious", int(values["body_count"]), True),
        ("correctness", int(values["correctness_body_count"]), False),
    ):
        repeat = int(values["repeat"]) if run_kind == "serious" else 1
        warmup = int(values["warmup"]) if run_kind == "serious" else 0
        for version, version_info in versions.items():
            root = Path(version_info["root"])
            env = _env_for(root, tag_native_optix_build=bool(version_info["tag_native_optix_build"]))
            command = [
                _python(root),
                str(Path(__file__).resolve()),
                "--worker",
                "--route",
                str(version_info["route"]),
                "--body-count",
                str(body_count),
                "--theta",
                "0.5",
                "--bucket-size",
                "32",
                "--max-depth",
                "32",
                "--repeat",
                str(repeat),
                "--warmup",
                str(warmup),
                "--frontier-capacity-multiplier",
                str(values["frontier_capacity_multiplier"]),
                "--partner",
                args.partner,
            ]
            if skip_validation:
                command.append("--skip-validation")
            executions.append(
                _run_command(
                    version=version,
                    run_kind=run_kind,
                    command=command,
                    cwd=ROOT,
                    env=env,
                    out_dir=out_dir,
                    timeout_sec=int(values["timeout_sec"]),
                )
            )
    summary = _analyze(executions, args.profile, args.partner)
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if all(int(item["returncode"]) == 0 for item in executions) else 1


if __name__ == "__main__":
    raise SystemExit(main())
