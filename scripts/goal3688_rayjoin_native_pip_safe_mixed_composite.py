#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import time
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt  # noqa: E402
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import run_cupy_baseline  # noqa: E402
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import run_rtdl_optix  # noqa: E402
from scripts.goal3609_rayjoin_recommended_mixed_route_composite import _claim_boundary  # noqa: E402
from scripts.goal3609_rayjoin_recommended_mixed_route_composite import _datasets_for_count  # noqa: E402
from scripts.goal3609_rayjoin_recommended_mixed_route_composite import _parse_counts  # noqa: E402
from scripts.goal3612_rayjoin_safe_mixed_route_composite import _run_exact_lsi_prepared_optix  # noqa: E402


SCHEMA = "rtdl.goal3688.rayjoin_native_pip_safe_mixed_composite.v1"
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal3688_rayjoin_native_pip_safe_mixed_composite_a5000" / "summary.json"
WORKLOADS = ("pip", "lsi", "overlay_seed")
SCOPED_SOURCE_PATHS = (
    "scripts/goal3688_rayjoin_native_pip_safe_mixed_composite.py",
    "tests/goal3688_rayjoin_native_pip_safe_mixed_composite_test.py",
    "scripts/goal3677_rayjoin_pip_relation_status_exact_count_timing.py",
    "tests/goal3686_resident_native_scalar_count_executor_test.py",
    "src/native/optix/rtdl_optix_api.cpp",
    "src/native/optix/rtdl_optix_prelude.h",
    "src/native/optix/rtdl_optix_workloads.cpp",
    "src/rtdsl/optix_runtime.py",
)


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    if not ordered:
        raise ValueError("cannot summarize empty timings")
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[mid])
    return float((ordered[mid - 1] + ordered[mid]) / 2.0)


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
            f"[goal3688] {label} {'warmup' if is_warmup else 'repeat'} "
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


def _run_native_pip_scalar_count(dataset: str, *, repeat: int, warmup: int, point_eps: float) -> dict[str, object]:
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    payload = rt.load_cdb(dataset)
    points = tuple(rt.chains_to_probe_points(payload))
    shapes = tuple(rt.chains_to_polygons(payload))
    prepare_start = time.perf_counter()
    prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
    prepare_static_scene_sec = time.perf_counter() - prepare_start
    prepare_points_start = time.perf_counter()
    prepared_points = prepared.prepare_point_probe_columns(points)
    prepare_point_columns_sec = time.perf_counter() - prepare_points_start
    executor_start = time.perf_counter()
    executor = prepared.prepare_relation_status_corrected_scalar_count_executor(
        prepared_points,
        point_eps=point_eps,
    )
    prepare_executor_sec = time.perf_counter() - executor_start
    try:
        def sync() -> None:
            return None

        def run_once() -> dict[str, Any]:
            result = executor.run()
            return {
                "row_count": int(result["row_count"]),
                "candidate_row_count": int(result["candidate_row_count"]),
                "boundary_candidate_row_count": int(result["boundary_candidate_row_count"]),
                "dropped_candidate_row_count": int(result["dropped_candidate_row_count"]),
                "native_traversal_seconds": float(result["traversal_seconds"]),
                "row_stream_materialized": bool(result["row_stream_materialized"]),
                "boundary_candidate_row_stream_materialized": bool(
                    result["boundary_candidate_row_stream_materialized"]
                ),
                "reusable_native_executor_used": bool(result["reusable_native_executor_used"]),
            }

        timing = _time_repeated(
            label="pip_native_relation_status_corrected_scalar_count",
            warmup=warmup,
            repeat=repeat,
            synchronize=sync,
            fn=run_once,
            stability_key="row_count",
        )
        return {
            "backend": "optix",
            "execution_route": "prepared_native_relation_status_corrected_scalar_count_executor",
            "rt_core_accelerated": True,
            "partner_accelerated": False,
            "dataset": dataset,
            "output_contract": "closed_shape_membership_scalar_count",
            "prepare_sec": {
                "prepare_static_scene_sec": prepare_static_scene_sec,
                "prepare_point_columns_sec": prepare_point_columns_sec,
                "prepare_executor_sec": prepare_executor_sec,
            },
            "hot_median_sec": float(timing["hot_median_sec"]),
            "hot_total_sec": float(timing["hot_total_sec"]),
            "hot_repeat": int(timing["hot_repeat"]),
            "hot_warmup": int(timing["hot_warmup"]),
            "row_count": int(timing["stability_value"]),
            "candidate_row_count": int(timing["runs"][-1]["candidate_row_count"]),
            "boundary_candidate_row_count": int(timing["runs"][-1]["boundary_candidate_row_count"]),
            "dropped_candidate_row_count": int(timing["runs"][-1]["dropped_candidate_row_count"]),
            "row_stream_materialized": False,
            "boundary_candidate_row_stream_materialized": False,
            "same_contract_route_reason": (
                "Goal3684/3686 native scalar correction validates boundary contacts in the generic "
                "OptiX relation-status pipeline and avoids dense boundary-row materialization."
            ),
            "timing": timing,
            "claim_boundary": _claim_boundary(),
        }
    finally:
        executor.close()
        prepared_points.close()
        prepared.close()


def run_composite(args: argparse.Namespace) -> dict[str, object]:
    counts = _parse_counts(args.counts)
    rows = []
    for count in counts:
        print(f"[goal3688] materialize count={count}", flush=True)
        datasets = _datasets_for_count(
            data_dir=args.data_dir,
            county_source=args.county_source_cdb,
            soil_source=args.soil_source_cdb,
            start=args.start,
            count=count,
        )
        cupy_rows: dict[str, dict[str, object]] = {}
        recommended_rows: dict[str, dict[str, object]] = {}
        for workload in WORKLOADS:
            print(f"[goal3688] count={count} workload={workload} CuPy baseline start", flush=True)
            cupy_rows[workload] = run_cupy_baseline(
                workload,
                datasets[workload],
                repeat=args.repeat,
                warmup=args.warmup,
            )
        print(f"[goal3688] count={count} workload=pip native scalar route start", flush=True)
        recommended_rows["pip"] = _run_native_pip_scalar_count(
            datasets["pip"],
            repeat=args.repeat,
            warmup=args.warmup,
            point_eps=float(args.point_eps),
        )
        print(f"[goal3688] count={count} workload=lsi exact RTDL/OptiX route start", flush=True)
        recommended_rows["lsi"] = _run_exact_lsi_prepared_optix(
            datasets["lsi"],
            repeat=args.repeat,
            warmup=args.warmup,
        )
        print(f"[goal3688] count={count} workload=overlay_seed RTDL/OptiX active-count route start", flush=True)
        recommended_rows["overlay_seed"] = run_rtdl_optix(
            "overlay_seed",
            datasets["overlay_seed"],
            repeat=args.repeat,
            warmup=args.warmup,
        )

        workload_rows = []
        for workload in WORKLOADS:
            cupy = cupy_rows[workload]
            recommended = recommended_rows[workload]
            recommended["claim_boundary"] = {
                **_claim_boundary(),
                **dict(recommended.get("claim_boundary", {})),
            }
            counts_match = int(cupy["row_count"]) == int(recommended["row_count"])
            if not counts_match:
                raise RuntimeError(
                    f"{workload} count mismatch at count={count}: "
                    f"CuPy={cupy['row_count']} recommended={recommended['row_count']}"
                )
            speedup = float(cupy["hot_median_sec"]) / float(recommended["hot_median_sec"])
            workload_rows.append(
                {
                    "workload": workload,
                    "dataset": datasets[workload],
                    "all_cupy_baseline": cupy,
                    "candidate_route": recommended,
                    "counts_match": counts_match,
                    "candidate_speedup_vs_cupy": speedup,
                    "candidate_backend": recommended.get("backend", "cupy"),
                    "candidate_route_kind": (
                        "rtdl_optix_native_scalar_count_executor"
                        if workload == "pip"
                        else (
                            "rtdl_optix_exact_refined_count"
                            if workload == "lsi"
                            else "rtdl_optix_active_count"
                        )
                    ),
                    "claim_boundary": _claim_boundary(),
                }
            )
        cupy_total = sum(float(row["all_cupy_baseline"]["hot_median_sec"]) for row in workload_rows)
        candidate_total = sum(float(row["candidate_route"]["hot_median_sec"]) for row in workload_rows)
        rows.append(
            {
                "chain_count": count,
                "datasets": datasets,
                "workloads": workload_rows,
                "all_cupy_sum_median_sec": cupy_total,
                "native_pip_safe_mixed_sum_median_sec": candidate_total,
                "native_pip_safe_mixed_speedup_vs_all_cupy": cupy_total / candidate_total,
                "all_counts_match": all(bool(row["counts_match"]) for row in workload_rows),
                "mix_definition": "unweighted sum of PIP, LSI, and overlay_seed hot median seconds",
                "claim_boundary": _claim_boundary(),
            }
        )
    ratios = [float(row["native_pip_safe_mixed_speedup_vs_all_cupy"]) for row in rows]
    return {
        "schema": SCHEMA,
        "goal": 3688,
        "generated_at_unix": time.time(),
        "git_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "source_commit_short": _command_output(["git", "rev-parse", "--short", "HEAD"]),
        "git_status_short": _command_output(["git", "status", "--short"]),
        "goal3688_scoped_source_paths": list(SCOPED_SOURCE_PATHS),
        "goal3688_scoped_source_status_short": _command_output(
            ["git", "status", "--short", "--", *SCOPED_SOURCE_PATHS]
        ),
        "goal3688_scoped_source_dirty": bool(
            _command_output(["git", "status", "--short", "--", *SCOPED_SOURCE_PATHS])
        ),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "start": int(args.start),
        "counts": list(counts),
        "repeat": int(args.repeat),
        "warmup": int(args.warmup),
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "all_counts_match": all(bool(row["all_counts_match"]) for row in rows),
            "geomean_native_pip_safe_mixed_speedup_vs_all_cupy": (
                math.prod(ratios) ** (1.0 / len(ratios)) if ratios else None
            ),
            "min_native_pip_safe_mixed_speedup_vs_all_cupy": min(ratios) if ratios else None,
        },
        "interpretation": (
            "Internal RayJoin candidate composite: PIP uses the Goal3686 native relation-status "
            "corrected scalar-count executor, LSI uses exact prepared RTDL/OptiX count with host "
            "double refinement, and overlay_seed uses RTDL/OptiX active-count. This packet does "
            "not promote a default route; it measures whether the new generic PIP scalar primitive "
            "can replace the older CuPy PIP leg in the same-contract composite."
        ),
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3688 RayJoin native-PIP safe mixed composite.")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "rayjoin_public_cdb")
    parser.add_argument("--county-source-cdb", type=Path, default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb")
    parser.add_argument("--soil-source-cdb", type=Path, default=ROOT / "data" / "rayjoin_public_cdb" / "br_soil.cdb")
    parser.add_argument("--start", type=int, default=256)
    parser.add_argument("--counts", default="4096")
    parser.add_argument("--repeat", type=int, default=20)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--point-eps", type=float, default=1.0e-9)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.repeat <= 0:
        raise ValueError("--repeat must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")
    if args.point_eps < 0.0:
        raise ValueError("--point-eps must be non-negative")
    return args


def main() -> int:
    args = parse_args()
    payload = run_composite(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3688] wrote {args.output}", flush=True)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
