from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Callable


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402


SCHEMA = "rtdl.goal3677.rayjoin_pip_relation_status_exact_count_timing.v1"


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _claim_boundary() -> dict[str, bool]:
    return {
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rayjoin_paper_reproduction_claim_authorized": False,
        "rtdl_beats_rayjoin_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "native_default_route_authorized": False,
    }


def _scoped_source_dirty() -> bool:
    paths = [
        "src/native/optix/rtdl_optix_core.cpp",
        "src/native/optix/rtdl_optix_workloads.cpp",
        "src/native/optix/rtdl_optix_api.cpp",
        "src/native/optix/rtdl_optix_prelude.h",
        "src/rtdsl/optix_runtime.py",
        "src/rtdsl/closed_shape_topology.py",
        "scripts/goal3677_rayjoin_pip_relation_status_exact_count_timing.py",
        "tests/goal3677_relation_status_filtered_exact_count_test.py",
        "docs/reports/goal3677_relation_status_filtered_exact_count_2026-06-06.md",
        "docs/handoff/HANDOFF_GEMINI_GOAL3677_RELATION_STATUS_EXACT_COUNT_REVIEW_2026-06-06.md",
    ]
    return bool(_command_output(["git", "status", "--short", "--", *paths]))


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("cannot summarize an empty timing series")
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[middle])
    return float((ordered[middle - 1] + ordered[middle]) / 2.0)


def _pair_counter(rows: tuple[dict[str, int], ...]) -> Counter[tuple[int, int]]:
    return Counter((int(row["point_id"]), int(row["shape_id"])) for row in rows)


def _time_repeated(
    *,
    label: str,
    warmup: int,
    repeat: int,
    synchronize: Callable[[], None],
    fn: Callable[[], dict[str, Any]],
    stability_key: str,
) -> dict[str, Any]:
    measured: list[float] = []
    values: list[int] = []
    runs: list[dict[str, Any]] = []
    for index in range(warmup + repeat):
        synchronize()
        start = time.perf_counter()
        result = fn()
        synchronize()
        elapsed = time.perf_counter() - start
        value = int(result[stability_key])
        is_warmup = index < warmup
        print(
            f"[goal3677] {label} {'warmup' if is_warmup else 'repeat'} "
            f"{index + 1}/{warmup + repeat} elapsed={elapsed:.6f}s {stability_key}={value}",
            flush=True,
        )
        runs.append(
            {
                "iteration": index,
                "is_warmup": is_warmup,
                "elapsed_sec": elapsed,
                stability_key: value,
                **{key: val for key, val in result.items() if key != stability_key},
            }
        )
        if not is_warmup:
            measured.append(elapsed)
            values.append(value)
    if len(set(values)) != 1:
        raise RuntimeError(f"{label} changed {stability_key} across repeats: {values}")
    return {
        "hot_median_sec": _median(measured),
        "hot_total_sec": float(sum(measured)),
        "hot_repeat_secs": measured,
        "hot_repeat": repeat,
        "hot_warmup": warmup,
        "stability_key": stability_key,
        "stability_value": values[-1] if values else None,
        "runs": runs,
    }


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    import cupy as cp  # type: ignore
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    dataset = rt.load_cdb(args.dataset)
    points = tuple(rt.chains_to_probe_points(dataset))
    shapes = tuple(rt.chains_to_polygons(dataset))
    print(
        f"[goal3677] loaded dataset points={len(points)} shapes={len(shapes)} "
        f"eps={os.environ.get('RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS')}",
        flush=True,
    )

    prepare_start = time.perf_counter()
    prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
    prepare_static_scene_sec = time.perf_counter() - prepare_start
    prepared_points_start = time.perf_counter()
    prepared_points = prepared.prepare_point_probe_columns(points)
    prepare_point_columns_sec = time.perf_counter() - prepared_points_start
    refiner_start = time.perf_counter()
    refiner = rt.prepare_closed_shape_membership_candidate_refiner_exact_cupy(
        points,
        shapes,
        point_eps=float(args.point_eps),
    )
    prepare_refiner_sec = time.perf_counter() - refiner_start

    try:
        print("[goal3677] generating exact oracle once", flush=True)
        exact_start = time.perf_counter()
        exact_rows = tuple(prepared.run(points))
        exact_sec = time.perf_counter() - exact_start
        exact_count = len(exact_rows)
        exact_pairs = _pair_counter(exact_rows)

        def sync() -> None:
            cp.cuda.Stream.null.synchronize()

        def count_all_candidates_once() -> dict[str, Any]:
            columns = prepared.relation_status_candidate_device_columns_prepared_points(
                prepared_points,
                relation_status_filter=0,
                max_rows=0,
            )
            try:
                return {
                    "candidate_count": int(columns.candidate_event_count),
                    "native_traversal_seconds": float(columns.traversal_seconds),
                }
            finally:
                columns.close()

        all_candidate_count_timing = _time_repeated(
            label="relation_status_all_candidate_count_only",
            warmup=int(args.warmup),
            repeat=int(args.repeat),
            synchronize=sync,
            fn=count_all_candidates_once,
            stability_key="candidate_count",
        )

        def boundary_rows_once() -> dict[str, Any]:
            columns = prepared.relation_status_candidate_device_columns_prepared_points(
                prepared_points,
                relation_status_filter=2,
                max_rows=int(args.boundary_max_rows),
            )
            try:
                columns.raise_if_overflowed(operation="boundary relation-status candidate stream")
                return {
                    "boundary_candidate_count": int(columns.row_count),
                    "required_capacity": int(columns.candidate_event_count),
                    "native_traversal_seconds": float(columns.traversal_seconds),
                }
            finally:
                columns.close()

        boundary_candidate_timing = _time_repeated(
            label="relation_status_boundary_candidate_columns",
            warmup=int(args.warmup),
            repeat=int(args.repeat),
            synchronize=sync,
            fn=boundary_rows_once,
            stability_key="boundary_candidate_count",
        )

        def corrected_count_once() -> dict[str, Any]:
            result = refiner.count_relation_status_corrected_prepared_points_numba(
                prepared,
                prepared_points,
                boundary_max_rows=int(args.boundary_max_rows),
                validate_columns=False,
            )
            return {
                "row_count": int(result["row_count"]),
                "candidate_row_count": int(result["candidate_row_count"]),
                "boundary_candidate_row_count": int(result["boundary_candidate_row_count"]),
                "dropped_candidate_row_count": int(result["dropped_candidate_row_count"]),
                "all_candidate_traversal_seconds": float(result["all_candidate_traversal_seconds"]),
                "boundary_candidate_traversal_seconds": float(result["boundary_candidate_traversal_seconds"]),
            }

        corrected_count_timing = _time_repeated(
            label="relation_status_corrected_exact_numba_count",
            warmup=int(args.warmup),
            repeat=int(args.repeat),
            synchronize=sync,
            fn=corrected_count_once,
            stability_key="row_count",
        )

        correctness_columns = prepared.relation_status_candidate_device_columns_prepared_points(
            prepared_points,
            relation_status_filter=2,
            max_rows=int(args.boundary_max_rows),
        )
        try:
            boundary_result = refiner.count_boundary_contacts_numba(correctness_columns, validate_columns=False)
            corrected_count = int(all_candidate_count_timing["stability_value"]) - int(
                boundary_result["dropped_candidate_row_count"]
            )
        finally:
            correctness_columns.close()

        return {
            "schema": SCHEMA,
            "dataset": str(Path(args.dataset).resolve()),
            "source_commit": _command_output(["git", "rev-parse", "HEAD"]),
            "source_commit_short": _command_output(["git", "rev-parse", "--short", "HEAD"]),
            "git_status_dirty": bool(_command_output(["git", "status", "--short"])),
            "goal3677_scoped_source_dirty": _scoped_source_dirty(),
            "pod_gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
            "environment": {
                "RTDL_OPTIX_LIBRARY": os.environ.get("RTDL_OPTIX_LIBRARY"),
                "RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS": os.environ.get(
                    "RTDL_OPTIX_POINT_PRIMITIVE_DEVICE_PREDICATE_EPS"
                ),
            },
            "point_count": len(points),
            "shape_count": len(shapes),
            "exact_oracle_count": exact_count,
            "exact_oracle_sec": exact_sec,
            "prepare_static_scene_sec": prepare_static_scene_sec,
            "prepare_point_columns_sec": prepare_point_columns_sec,
            "prepare_refiner_sec": prepare_refiner_sec,
            "timings": {
                "all_candidate_count_only": all_candidate_count_timing,
                "boundary_candidate_columns": boundary_candidate_timing,
                "relation_status_corrected_exact_numba_count": corrected_count_timing,
            },
            "correctness": {
                "exact_count": exact_count,
                "corrected_count": corrected_count,
                "all_match_exact_count": corrected_count == exact_count,
                "exact_pair_multiset_rows_materialized_for_oracle": len(exact_pairs),
            },
            "boundary_result": {
                key: value
                for key, value in boundary_result.items()
                if isinstance(value, (str, int, float, bool))
            },
            "claim_boundary": _claim_boundary(),
            "notes": (
                "This packet composes generic relation-status filtered candidate streams with a Numba "
                "boundary-contact scalar continuation. It does not claim RayJoin reproduction, public "
                "speedup, true zero-copy, or default route authorization."
            ),
        }
    finally:
        prepared_points.close()
        prepared.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county_start0_count16545.cdb",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--repeat", type=int, default=10)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--boundary-max-rows", type=int, default=65536)
    parser.add_argument("--point-eps", type=float, default=1.0e-9)
    args = parser.parse_args()
    result = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3677] wrote {args.output}", flush=True)
    print(json.dumps(result["correctness"], indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
