from __future__ import annotations

import argparse
import json
import math
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from rtdsl.rayjoin_numba_auto_planner import RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA
from rtdsl.rayjoin_paper_suite import availability_matrix
from rtdsl.rayjoin_paper_suite import dataset_file
from rtdsl.rayjoin_paper_suite import paper_pairs


def _split_csv(value: str | None, *, default: Iterable[str]) -> tuple[str, ...]:
    if value is None or value.strip() == "":
        return tuple(default)
    return tuple(part.strip() for part in value.split(",") if part.strip())


def _rt_core_status() -> dict[str, object]:
    try:
        completed = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return {"rt_core_likely": False, "gpu_names": [], "error": str(exc)}
    rows = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    names = [row.split(",", 1)[0].strip() for row in rows]
    rt_markers = ("RTX", "L4", "L40", "A10", "A16", "A40", "A4000", "A5000", "A6000", "T4")
    return {
        "rt_core_likely": any(any(marker in name.upper() for marker in rt_markers) for name in names),
        "gpu_names": names,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _median(values: list[float]) -> float | None:
    return statistics.median(values) if values else None


def _candidate_status_from_stage(
    *,
    stage_counts_pass: bool,
    topology_geometry_hash_match_confirmed: bool,
) -> tuple[str, bool]:
    if topology_geometry_hash_match_confirmed and stage_counts_pass:
        return "pass", True
    if stage_counts_pass:
        return "stage_count_pass_full_overlay_hash_not_confirmed", False
    return "fail", False


def _numba_lsi_stream_digest_kernel():
    from numba import cuda  # type: ignore

    @cuda.jit
    def _kernel(left_ids, right_ids, xs, ys, partials, row_count, scale):
        worker = cuda.grid(1)
        stride = cuda.gridsize(1)
        local_count = 0
        local_left_sum = 0
        local_right_sum = 0
        local_x_micro_sum = 0
        local_y_micro_sum = 0
        local_nonfinite = 0
        for index in range(worker, row_count, stride):
            x_value = xs[index]
            y_value = ys[index]
            local_count += 1
            local_left_sum += left_ids[index]
            local_right_sum += right_ids[index]
            if (
                x_value == x_value
                and y_value == y_value
                and math.fabs(x_value) < 1.0e300
                and math.fabs(y_value) < 1.0e300
            ):
                local_x_micro_sum += int(x_value * scale)
                local_y_micro_sum += int(y_value * scale)
            else:
                local_nonfinite += 1
        partials[worker, 0] = local_count
        partials[worker, 1] = local_left_sum
        partials[worker, 2] = local_right_sum
        partials[worker, 3] = local_x_micro_sum
        partials[worker, 4] = local_y_micro_sum
        partials[worker, 5] = local_nonfinite

    return _kernel


def _run_numba_lsi_stream_digest(
    *,
    left_ids,
    right_ids,
    intersection_x,
    intersection_y,
    row_count: int,
    cuda,
    np,
    block_size: int = 128,
    worker_blocks: int = 256,
    coordinate_scale: int = 1_000_000,
) -> dict[str, object]:
    row_count = int(row_count)
    if row_count < 0:
        raise ValueError("row_count must be non-negative")
    worker_count = max(1, min(int(worker_blocks) * int(block_size), max(1, row_count)))
    partials = cuda.device_array((worker_count, 6), dtype=np.int64)
    partials.copy_to_device(np.zeros((worker_count, 6), dtype=np.int64))
    cuda.synchronize()
    started = time.perf_counter()
    if row_count:
        grid = ((worker_count + int(block_size) - 1) // int(block_size),)
        _numba_lsi_stream_digest_kernel()[grid, int(block_size)](
            left_ids,
            right_ids,
            intersection_x,
            intersection_y,
            partials,
            row_count,
            int(coordinate_scale),
        )
    cuda.synchronize()
    elapsed = time.perf_counter() - started
    partial_host = partials.copy_to_host()
    totals = partial_host.sum(axis=0)
    return {
        "elapsed_sec": elapsed,
        "coordinate_scale": int(coordinate_scale),
        "worker_count": int(worker_count),
        "row_count": int(totals[0]),
        "left_id_sum": int(totals[1]),
        "right_id_sum": int(totals[2]),
        "intersection_x_micro_sum": int(totals[3]),
        "intersection_y_micro_sum": int(totals[4]),
        "nonfinite_intersection_points": int(totals[5]),
        "host_row_materialization_used": False,
        "host_digest_result_materialization_used": True,
    }


def _run_segmented_count_probe(
    *,
    pair_id: str,
    dataset_root: Path,
    warmup: int,
    repeat: int,
    topology_geometry_hash_match_confirmed: bool,
) -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    from rtdsl.numba_partner_continuation import _as_numba_cuda_vector
    from rtdsl.numba_partner_continuation import _import_numba_stack
    from rtdsl.numba_partner_continuation import run_numba_compact_mask_i64
    from rtdsl.numba_partner_continuation import run_numba_segmented_count_i64
    from rtdsl.optix_runtime import prepare_segment_pair_intersection_optix
    from rtdsl.optix_runtime import prepare_segment_pair_left_set_optix
    from rtdsl.rayjoin_overlay import _rayjoin_lsi_predicate_env
    from rtdsl.rayjoin_overlay import load_cdb_overlay_packed_inputs

    pair = next(pair for pair in paper_pairs() if pair.pair_id == pair_id)
    left_inputs = load_cdb_overlay_packed_inputs(dataset_file(dataset_root, pair.left_relative_path))
    right_inputs = load_cdb_overlay_packed_inputs(dataset_file(dataset_root, pair.right_relative_path))
    cuda, np = _import_numba_stack()
    import cupy as cp  # type: ignore

    prepared = None
    prepared_left = None
    try:
        with _rayjoin_lsi_predicate_env("optix"):
            prepared = prepare_segment_pair_intersection_optix(right_inputs.segments)
            prepared_left = prepare_segment_pair_left_set_optix(left_inputs.segments)
            expected = prepared.count_prepared_left_exact_intersections(prepared_left)
            expected_count = int(expected["count"])
            segmented_runs: list[dict[str, object]] = []
            compact_runs: list[dict[str, object]] = []
            digest_runs: list[dict[str, object]] = []
            for iteration in range(int(warmup) + int(repeat)):
                is_warmup = iteration < int(warmup)
                columns = None
                try:
                    start = time.perf_counter()
                    columns = prepared.exact_device_columns_prepared_left(
                        prepared_left,
                        max_rows=expected_count,
                    )
                    cupy_columns = columns.as_cupy_columns()
                    intersection_point_columns_present = (
                        "intersection_point_x" in cupy_columns
                        and "intersection_point_y" in cupy_columns
                    )
                    left_ids = _as_numba_cuda_vector(
                        cupy_columns["left_id"],
                        name="left_id",
                        dtype=np.int64,
                        cuda=cuda,
                        np=np,
                    )
                    right_ids = _as_numba_cuda_vector(
                        cupy_columns["right_id"],
                        name="right_id",
                        dtype=np.int64,
                        cuda=cuda,
                        np=np,
                    )
                    intersection_x = _as_numba_cuda_vector(
                        cupy_columns["intersection_point_x"],
                        name="intersection_point_x",
                        dtype=np.float64,
                        cuda=cuda,
                        np=np,
                    )
                    intersection_y = _as_numba_cuda_vector(
                        cupy_columns["intersection_point_y"],
                        name="intersection_point_y",
                        dtype=np.float64,
                        cuda=cuda,
                        np=np,
                    )
                    segmented = run_numba_segmented_count_i64(
                        left_ids,
                        group_count=int(left_inputs.edge_count) + 1,
                        validate_group_ids=False,
                    )
                    cuda.synchronize()
                    segmented_wall = time.perf_counter() - start
                    counts = segmented["outputs"]["counts"].copy_to_host()
                    count_sum = int(counts.sum())
                    segmented_runs.append(
                        {
                            "iteration": iteration,
                            "is_warmup": is_warmup,
                            "wall_sec": segmented_wall,
                            "candidate_column_traversal_sec": float(columns.traversal_seconds),
                            "numba_elapsed_sec": float(
                                segmented["phase_timing"]["phases_sec"]["partner_continuation"]
                            ),
                            "candidate_row_count": int(columns.row_count),
                            "expected_lsi_count": expected_count,
                            "primitive_source": "exact_device_columns_prepared_left",
                            "native_symbol": columns.native_symbol,
                            "intersection_point_columns_present": intersection_point_columns_present,
                            "segmented_count_sum": count_sum,
                            "stage_counts_pass": (
                                int(columns.row_count) == expected_count
                                and count_sum == expected_count
                                and not bool(columns.overflow)
                            ),
                        }
                    )
                    digest = _run_numba_lsi_stream_digest(
                        left_ids=left_ids,
                        right_ids=right_ids,
                        intersection_x=intersection_x,
                        intersection_y=intersection_y,
                        row_count=int(columns.row_count),
                        cuda=cuda,
                        np=np,
                    )
                    digest_runs.append(
                        {
                            "iteration": iteration,
                            "is_warmup": is_warmup,
                            "wall_sec": float(digest["elapsed_sec"]),
                            "candidate_column_traversal_sec": float(columns.traversal_seconds),
                            "candidate_row_count": int(columns.row_count),
                            "expected_lsi_count": expected_count,
                            "primitive_source": "exact_device_columns_prepared_left",
                            "native_symbol": columns.native_symbol,
                            "intersection_point_columns_present": intersection_point_columns_present,
                            "stream_digest": digest,
                            "stage_counts_pass": (
                                int(columns.row_count) == expected_count
                                and int(digest["row_count"]) == expected_count
                                and int(digest["nonfinite_intersection_points"]) == 0
                                and not bool(columns.overflow)
                            ),
                        }
                    )

                    mask = _as_numba_cuda_vector(
                        cp.ones((int(columns.row_count),), dtype=cp.bool_),
                        name="mask",
                        dtype=np.bool_,
                        cuda=cuda,
                        np=np,
                    )
                    compact_start = time.perf_counter()
                    compact = run_numba_compact_mask_i64(right_ids, mask)
                    cuda.synchronize()
                    compact_wall = time.perf_counter() - compact_start
                    compact_count = int(compact["outputs"]["values"].shape[0])
                    compact_runs.append(
                        {
                            "iteration": iteration,
                            "is_warmup": is_warmup,
                            "wall_sec": compact_wall,
                            "numba_elapsed_sec": float(
                                compact["phase_timing"]["phases_sec"]["partner_continuation"]
                            ),
                            "candidate_row_count": int(columns.row_count),
                            "expected_lsi_count": expected_count,
                            "primitive_source": "exact_device_columns_prepared_left",
                            "native_symbol": columns.native_symbol,
                            "intersection_point_columns_present": intersection_point_columns_present,
                            "compact_count": compact_count,
                            "stage_counts_pass": compact_count == expected_count,
                            "host_prefix_sum_used": bool(compact.get("host_prefix_sum_used", True)),
                        }
                    )
                finally:
                    if columns is not None:
                        columns.close()
        hot_segmented = [run for run in segmented_runs if not run["is_warmup"]]
        hot_compact = [run for run in compact_runs if not run["is_warmup"]]
        hot_digest = [run for run in digest_runs if not run["is_warmup"]]
        segmented_pass = all(bool(run["stage_counts_pass"]) for run in hot_segmented)
        compact_pass = all(bool(run["stage_counts_pass"]) for run in hot_compact)
        digest_pass = all(bool(run["stage_counts_pass"]) for run in hot_digest)
        segmented_correctness, segmented_hash = _candidate_status_from_stage(
            stage_counts_pass=segmented_pass,
            topology_geometry_hash_match_confirmed=topology_geometry_hash_match_confirmed,
        )
        compact_correctness, compact_hash = _candidate_status_from_stage(
            stage_counts_pass=compact_pass,
            topology_geometry_hash_match_confirmed=topology_geometry_hash_match_confirmed,
        )
        digest_correctness, digest_hash = _candidate_status_from_stage(
            stage_counts_pass=digest_pass,
            topology_geometry_hash_match_confirmed=topology_geometry_hash_match_confirmed,
        )
        segmented_total = _median([float(run["wall_sec"]) for run in hot_segmented])
        compact_total = _median([float(run["wall_sec"]) for run in hot_compact])
        digest_total = _median([float(run["wall_sec"]) for run in hot_digest])
        common = {
            "pair_id": pair_id,
            "measurement_source": "pod_runtime",
            "device_column_route": True,
            "v2_14_lsi_count": expected_count,
            "measurement_scope": "v4_numba_post_traversal_candidate_stage",
            "full_polygon_overlay_hash_required_for_selector_pass": True,
        }
        segmented_row = {
            **common,
            "plan_id": "v4_numba_post_traversal_segmented_counts",
            "correctness_status": segmented_correctness,
            "measured_total_sec": segmented_total,
            "steady_state_sec": segmented_total,
            "compile_jit_sec": None,
            "topology_geometry_hash_match": segmented_hash,
            "host_materialization_in_hot_path": False,
            "runs": segmented_runs,
        }
        compact_row = {
            **common,
            "plan_id": "v4_numba_post_traversal_mask_compact",
            "correctness_status": compact_correctness,
            "measured_total_sec": compact_total,
            "steady_state_sec": compact_total,
            "compile_jit_sec": None,
            "topology_geometry_hash_match": compact_hash,
            "host_materialization_in_hot_path": True,
            "runs": compact_runs,
        }
        digest_row = {
            **common,
            "plan_id": "v4_numba_post_traversal_lsi_stream_digest",
            "correctness_status": digest_correctness,
            "measured_total_sec": digest_total,
            "steady_state_sec": digest_total,
            "compile_jit_sec": None,
            "topology_geometry_hash_match": digest_hash,
            "host_materialization_in_hot_path": False,
            "host_row_materialization_used": False,
            "host_digest_result_materialization_used": True,
            "runs": digest_runs,
        }
        return segmented_row, compact_row, digest_row
    finally:
        if prepared_left is not None:
            prepared_left.close()
        if prepared is not None:
            prepared.close()


def build_dry_run_payload(args: argparse.Namespace) -> dict[str, object]:
    pair_ids = _split_csv(args.pairs, default=[pair.pair_id for pair in paper_pairs()])
    availability = availability_matrix(args.dataset_root, pair_ids=pair_ids, program_ids=("overlay",))
    return {
        "schema": RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA,
        "status": "dry_run",
        "dataset_root": str(args.dataset_root),
        "warmup": int(args.warmup),
        "repeat": int(args.repeat),
        "rows": [],
        "planned_pairs": [
            {
                "pair_id": row.pair_id,
                "paper_label": row.paper_label,
                "exact_input_ready": bool(row.exact_input_ready),
                "blocker": row.blocker,
                "candidate_plans": (
                    "v4_numba_post_traversal_segmented_counts",
                    "v4_numba_post_traversal_mask_compact",
                    "v4_numba_post_traversal_lsi_stream_digest",
                ),
            }
            for row in availability
        ],
        "claim_boundary": (
            "Dry run does not measure performance. Real rows require an RT-core POD, "
            "current OptiX backend device-column symbols, and Numba CUDA."
        ),
    }


def build_probe_payload(args: argparse.Namespace) -> dict[str, object]:
    pair_ids = _split_csv(args.pairs, default=[pair.pair_id for pair in paper_pairs()])
    availability = availability_matrix(args.dataset_root, pair_ids=pair_ids, program_ids=("overlay",))
    rows: list[dict[str, object]] = []
    blockers: list[dict[str, object]] = []
    rt_core = _rt_core_status()
    if not bool(rt_core["rt_core_likely"]) and not args.allow_non_rt_gpu:
        return {
            "schema": RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA,
            "status": "blocked_non_rt_gpu",
            "dataset_root": str(args.dataset_root),
            "rows": [],
            "blockers": [{"reason": "rt_core_gpu_not_detected", "gpu": rt_core}],
            "claim_boundary": "No performance row is emitted without an RT-core GPU.",
        }
    for available in availability:
        if not available.exact_input_ready:
            blockers.append(
                {
                    "pair_id": available.pair_id,
                    "reason": "missing_exact_section57_cdb_inputs",
                    "blocker": available.blocker,
                }
            )
            continue
        try:
            segmented, compact, digest = _run_segmented_count_probe(
                pair_id=available.pair_id,
                dataset_root=args.dataset_root,
                warmup=args.warmup,
                repeat=args.repeat,
                topology_geometry_hash_match_confirmed=args.topology_geometry_hash_match_confirmed,
            )
        except Exception as exc:
            blockers.append(
                {
                    "pair_id": available.pair_id,
                    "reason": "candidate_probe_failed",
                    "error": repr(exc),
                }
            )
            continue
        rows.extend([segmented, compact, digest])
    return {
        "schema": RAYJOIN_SECTION57_NUMBA_MEASURED_CANDIDATES_SCHEMA,
        "status": "measured" if rows else "no_rows_measured",
        "dataset_root": str(args.dataset_root),
        "warmup": int(args.warmup),
        "repeat": int(args.repeat),
        "rt_core": rt_core,
        "rows": rows,
        "blockers": blockers,
        "claim_boundary": (
            "Rows are candidate-stage V4+Numba measurements. The selector accepts "
            "only rows with correctness_status='pass', confirmed topology/geometry "
            "hash match, device-column route, and no host materialization in the hot path."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure RayJoin Section 5.7 V4+Numba candidate continuations on a POD."
    )
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--pairs")
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--topology-geometry-hash-match-confirmed",
        action="store_true",
        help="Allow full selector-pass correctness only after independent full-overlay hash comparison.",
    )
    parser.add_argument(
        "--allow-non-rt-gpu",
        action="store_true",
        help="Developer escape hatch for plumbing tests; public performance evidence still requires RT-core hardware.",
    )
    args = parser.parse_args()

    payload = build_dry_run_payload(args) if args.dry_run else build_probe_payload(args)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload.get("status") not in {"blocked_non_rt_gpu", "no_rows_measured"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
