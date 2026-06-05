from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _stats(values: list[float], *, skip_first: bool = True) -> dict[str, float]:
    sample = values[1:] if skip_first and len(values) > 1 else values
    return {
        "min": min(sample),
        "median": statistics.median(sample),
        "max": max(sample),
    }


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore
    from rtdsl.datasets import chains_to_polygons
    from rtdsl.datasets import chains_to_probe_points
    from rtdsl.datasets import load_cdb
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    county = load_cdb(args.county_cdb)
    points = tuple(chains_to_probe_points(county))
    shapes = tuple(chains_to_polygons(county))
    prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
    prepared_refiner = rt.prepare_closed_shape_membership_candidate_refiner_exact_cupy(
        points,
        shapes,
        point_eps=float(args.point_eps),
    )
    try:
        # Warm up OptiX, CuPy module compilation, and the prepared lookup path.
        warm_points = points[: min(len(points), 512)]
        warm_columns = prepared.candidate_device_columns(warm_points, max_rows=max(4096, len(warm_points) * 4))
        try:
            _ = rt.refine_closed_shape_membership_candidate_columns_exact_cupy(warm_columns, warm_points, shapes)
            cp.cuda.Stream.null.synchronize()
        finally:
            warm_columns.close()

        host_times: list[float] = []
        candidate_times: list[float] = []
        one_shot_refine_times: list[float] = []
        prepared_refine_times: list[float] = []
        one_shot_total_times: list[float] = []
        prepared_total_times: list[float] = []
        row_counts: list[int] = []
        candidate_counts: list[int] = []

        for index in range(int(args.iterations)):
            t0 = time.perf_counter()
            host_rows = prepared.run(points)
            t1 = time.perf_counter()
            columns = prepared.candidate_device_columns(points, max_rows=int(args.max_rows))
            cp.cuda.Stream.null.synchronize()
            t2 = time.perf_counter()
            one_shot = rt.refine_closed_shape_membership_candidate_columns_exact_cupy(
                columns,
                points,
                shapes,
                point_eps=float(args.point_eps),
            )
            cp.cuda.Stream.null.synchronize()
            t3 = time.perf_counter()
            prepared_result = prepared_refiner.refine(columns)
            cp.cuda.Stream.null.synchronize()
            t4 = time.perf_counter()
            columns.close()

            host_times.append(t1 - t0)
            candidate_times.append(t2 - t1)
            one_shot_refine_times.append(t3 - t2)
            prepared_refine_times.append(t4 - t3)
            one_shot_total_times.append(t3 - t1)
            prepared_total_times.append((t2 - t1) + (t4 - t3))
            row_counts.append(int(prepared_result["row_count"]))
            candidate_counts.append(int(prepared_result["candidate_row_count"]))
            if int(one_shot["row_count"]) != int(prepared_result["row_count"]):
                raise RuntimeError("one-shot and prepared CuPy refinement row counts diverged")
            print(
                "[goal3427] iteration "
                f"{index} host={host_times[-1]:.6f}s candidate={candidate_times[-1]:.6f}s "
                f"one_shot_refine={one_shot_refine_times[-1]:.6f}s "
                f"prepared_refine={prepared_refine_times[-1]:.6f}s rows={row_counts[-1]}",
                flush=True,
            )
    finally:
        prepared.close()

    host_stats = _stats(host_times)
    one_shot_refine_stats = _stats(one_shot_refine_times)
    prepared_refine_stats = _stats(prepared_refine_times)
    one_shot_total_stats = _stats(one_shot_total_times)
    prepared_total_stats = _stats(prepared_total_times)
    return {
        "schema": "rtdl.goal3427.prepared_cupy_refiner_timing_probe.v1",
        "goal": 3427,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "county_cdb": str(args.county_cdb),
        "point_count": len(points),
        "shape_count": len(shapes),
        "iterations": int(args.iterations),
        "host_exact_row_count": len(host_rows),
        "candidate_row_count": candidate_counts[-1],
        "prepared_refined_row_count": row_counts[-1],
        "all_prepared_counts_match_host": all(count == len(host_rows) for count in row_counts),
        "host_exact_sec": host_stats,
        "candidate_columns_sec": _stats(candidate_times),
        "one_shot_cupy_refine_sec": one_shot_refine_stats,
        "prepared_cupy_refine_sec": prepared_refine_stats,
        "one_shot_total_sec": one_shot_total_stats,
        "prepared_total_sec": prepared_total_stats,
        "prepared_refine_vs_one_shot_median": (
            prepared_refine_stats["median"] / one_shot_refine_stats["median"]
            if one_shot_refine_stats["median"]
            else None
        ),
        "prepared_total_vs_host_median": (
            prepared_total_stats["median"] / host_stats["median"]
            if host_stats["median"]
            else None
        ),
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "rayjoin_paper_reproduction_claim_authorized": False,
        },
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3427 prepared CuPy refiner timing probe.")
    parser.add_argument(
        "--county-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb",
    )
    parser.add_argument("--max-rows", type=int, default=60000)
    parser.add_argument("--iterations", type=int, default=6)
    parser.add_argument("--point-eps", type=float, default=1.0e-9)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
