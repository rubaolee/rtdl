#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import rtdsl as rt  # noqa: E402
from rtdsl.datasets import CdbDataset  # noqa: E402
from scripts.goal3589_rayjoin_cupy_same_contract_baseline import run_cupy_baseline  # noqa: E402


SCHEMA = "rtdl.goal3604.rayjoin_pip_boundary_event_signal_timing.v1"
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "goal3604_rayjoin_pip_boundary_event_signal_timing_a5000" / "summary.json"


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


def _median(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot summarize an empty timing list")
    ordered = sorted(values)
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return float(ordered[mid])
    return float((ordered[mid - 1] + ordered[mid]) / 2.0)


def _materialize_slice(source: Path, output: Path, *, start: int, count: int) -> Path:
    if output.exists():
        return output
    source_dataset = rt.load_cdb(source)
    sliced = CdbDataset(
        name=f"{source.stem}_start{start}_count{count}",
        chains=tuple(source_dataset.chains[start : start + count]),
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    rt.write_cdb(sliced, output)
    return output


def _parse_counts(value: str) -> tuple[int, ...]:
    counts = tuple(int(part.strip()) for part in value.split(",") if part.strip())
    if not counts:
        raise ValueError("--counts must not be empty")
    for count in counts:
        if count <= 0:
            raise ValueError("--counts values must be positive")
    return counts


def _pair_set(rows: tuple[dict[str, Any], ...]) -> set[tuple[int, int]]:
    return {(int(row["point_id"]), int(row["shape_id"])) for row in rows}


def _host_pairs(cp_module, point_ids, shape_ids) -> set[tuple[int, int]]:
    return set(
        zip(
            (int(value) for value in cp_module.asnumpy(point_ids).tolist()),
            (int(value) for value in cp_module.asnumpy(shape_ids).tolist()),
        )
    )


def _device_pair_key(cp, point_ids, shape_ids):
    if int(point_ids.size) == 0:
        return cp.asarray((), dtype=cp.int64), 0, 0, 1
    min_point = int(cp.min(point_ids).item())
    max_point = int(cp.max(point_ids).item())
    min_shape = int(cp.min(shape_ids).item())
    max_shape = int(cp.max(shape_ids).item())
    point_offset = -min_point if min_point < 0 else 0
    shape_offset = -min_shape if min_shape < 0 else 0
    base = max_shape + shape_offset + 1
    if base <= 0:
        raise OverflowError("shape key base must be positive")
    max_point_key = max_point + point_offset
    max_shape_key = max_shape + shape_offset
    int64_max = 9223372036854775807
    if max_point_key > (int64_max - max_shape_key) // base:
        raise OverflowError("point/shape ids are too large for int64 pair keys")
    return (point_ids + point_offset) * base + (shape_ids + shape_offset), point_offset, shape_offset, base


def _device_pair_key_with_offsets(point_ids, shape_ids, *, point_offset: int, shape_offset: int, base: int):
    return (point_ids + point_offset) * base + (shape_ids + shape_offset)


def _select_points_by_boundary_event_counts(cp, candidate_point_ids, candidate_shape_ids, boundary_point_ids, boundary_shape_ids, crossing_t):
    zero_mask = cp.abs(crossing_t) == 0.0
    if int(cp.count_nonzero(zero_mask).item()) == 0:
        candidate_keys, _point_offset, _shape_offset, _base = _device_pair_key(
            cp,
            candidate_point_ids,
            candidate_shape_ids,
        )
        zero_candidate_points = cp.asarray((), dtype=cp.int64)
    else:
        zero_points = boundary_point_ids[zero_mask]
        zero_shapes = boundary_shape_ids[zero_mask]
        combined_points = cp.concatenate((candidate_point_ids, zero_points))
        combined_shapes = cp.concatenate((candidate_shape_ids, zero_shapes))
        _combined_keys, point_offset, shape_offset, base = _device_pair_key(cp, combined_points, combined_shapes)
        candidate_keys = _device_pair_key_with_offsets(
            candidate_point_ids,
            candidate_shape_ids,
            point_offset=point_offset,
            shape_offset=shape_offset,
            base=base,
        )
        unique_candidate_keys = cp.sort(cp.unique(candidate_keys))
        zero_keys = _device_pair_key_with_offsets(
            zero_points,
            zero_shapes,
            point_offset=point_offset,
            shape_offset=shape_offset,
            base=base,
        )
        pos = cp.searchsorted(unique_candidate_keys, zero_keys)
        safe_pos = cp.minimum(pos, int(unique_candidate_keys.size) - 1)
        found = (pos < int(unique_candidate_keys.size)) & (unique_candidate_keys[safe_pos] == zero_keys)
        if int(cp.count_nonzero(found).item()) == 0:
            zero_candidate_points = cp.asarray((), dtype=cp.int64)
        else:
            matched_keys = cp.unique(zero_keys[found])
            zero_candidate_points = matched_keys // base - point_offset

    candidate_points, candidate_inverse = cp.unique(candidate_point_ids, return_inverse=True)
    candidate_counts = cp.bincount(candidate_inverse, minlength=int(candidate_points.size))
    if int(zero_candidate_points.size) == 0:
        zero_counts = cp.zeros_like(candidate_counts)
    else:
        zero_points, zero_inverse = cp.unique(zero_candidate_points, return_inverse=True)
        zero_counts_sparse = cp.bincount(zero_inverse, minlength=int(zero_points.size))
        pos = cp.searchsorted(zero_points, candidate_points)
        safe_pos = cp.minimum(pos, int(zero_points.size) - 1)
        found = (pos < int(zero_points.size)) & (zero_points[safe_pos] == candidate_points)
        zero_counts = cp.where(found, zero_counts_sparse[safe_pos], cp.asarray(0, dtype=zero_counts_sparse.dtype))
    selected_mask = (candidate_counts > zero_counts) & (zero_counts <= 2)
    return candidate_points[selected_mask].astype(cp.int64, copy=False)


def _time_repeated(*, label: str, repeat: int, warmup: int, sync, fn, stability_value) -> dict[str, object]:
    measured: list[float] = []
    values: list[int] = []
    runs: list[dict[str, object]] = []
    total = warmup + repeat
    for iteration in range(total):
        sync()
        start = time.perf_counter()
        value = fn()
        sync()
        elapsed = time.perf_counter() - start
        stable = int(stability_value(value))
        is_warmup = iteration < warmup
        print(
            f"[goal3604] {label} {'warmup' if is_warmup else 'repeat'} "
            f"{iteration + 1}/{total} elapsed={elapsed:.6f}s value={stable}",
            flush=True,
        )
        runs.append(
            {
                "iteration": iteration,
                "is_warmup": is_warmup,
                "elapsed_sec": elapsed,
                "stability_value": stable,
            }
        )
        if not is_warmup:
            measured.append(elapsed)
            values.append(stable)
    if len(set(values)) != 1:
        raise RuntimeError(f"{label} changed stability value across repeats: {values}")
    return {
        "hot_median_sec": _median(measured),
        "hot_total_sec": float(sum(measured)),
        "hot_repeat_secs": measured,
        "hot_repeat": repeat,
        "hot_warmup": warmup,
        "stability_value": values[-1] if values else 0,
        "runs": runs,
    }


def _run_boundary_event_signal_row(*, county_cdb: Path, repeat: int, warmup: int, crossing_tolerance: float) -> dict[str, object]:
    import cupy as cp  # type: ignore
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    county = rt.load_cdb(county_cdb)
    points = rt.chains_to_probe_points(county)
    shapes = rt.chains_to_polygons(county)
    prepare_start = time.perf_counter()
    prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
    prepare_sec = time.perf_counter() - prepare_start

    exact_rows = tuple(prepared.run(points))
    exact_pairs = _pair_set(exact_rows)
    exact_count = len(exact_pairs)

    def sync() -> None:
        cp.cuda.Stream.null.synchronize()

    def run_once():
        candidate_columns = None
        boundary_columns = None
        try:
            candidate_columns = prepared.candidate_device_columns(points)
            candidates = candidate_columns.as_cupy_columns()
            boundary_columns = prepared.first_boundary_crossing_device_columns(
                points,
                max_rows=len(points) * len(shapes),
            )
            boundary = boundary_columns.as_cupy_columns()
            selected_points = _select_points_by_boundary_event_counts(
                cp,
                candidates["point_id"],
                candidates["shape_id"],
                boundary["point_id"],
                boundary["shape_id"],
                boundary["crossing_t"],
            )
            filtered = rt.run_selective_closed_shape_boundary_event_membership_pipeline_cupy(
                candidate_point_ids=candidates["point_id"],
                candidate_shape_ids=candidates["shape_id"],
                boundary_point_ids=boundary["point_id"],
                boundary_shape_ids=boundary["shape_id"],
                boundary_crossing_t=boundary["crossing_t"],
                selected_point_ids=selected_points,
                crossing_tolerance=crossing_tolerance,
            )
            return {
                "filtered_count": int(filtered["point_id"].size),
                "selected_point_count": int(selected_points.size),
                "candidate_row_count": int(candidate_columns.row_count),
                "boundary_event_row_count": int(boundary_columns.row_count),
                "boundary_event_overflow": bool(boundary_columns.overflow),
                "candidate_overflow": bool(candidate_columns.overflow),
            }
        finally:
            if boundary_columns is not None:
                boundary_columns.close()
            if candidate_columns is not None:
                candidate_columns.close()

    timed = _time_repeated(
        label=f"pip/boundary_event_signal/{county_cdb.name}",
        repeat=repeat,
        warmup=warmup,
        sync=sync,
        fn=run_once,
        stability_value=lambda value: value["filtered_count"],
    )
    validation = run_once()
    prepared.close()
    return {
        "backend": "optix+cupy",
        "execution_route": "candidate_columns_plus_boundary_event_signal_selective_cupy_filter",
        "dataset": str(county_cdb),
        "point_count": len(points),
        "shape_count": len(shapes),
        "prepare_static_scene_sec": prepare_sec,
        "exact_row_count": exact_count,
        "filtered_row_count": int(validation["filtered_count"]),
        "counts_match_exact": int(validation["filtered_count"]) == exact_count,
        "selected_point_count": int(validation["selected_point_count"]),
        "candidate_row_count": int(validation["candidate_row_count"]),
        "boundary_event_row_count": int(validation["boundary_event_row_count"]),
        "candidate_overflow": bool(validation["candidate_overflow"]),
        "boundary_event_overflow": bool(validation["boundary_event_overflow"]),
        "crossing_tolerance": float(crossing_tolerance),
        "hot_median_sec": timed["hot_median_sec"],
        "hot_total_sec": timed["hot_total_sec"],
        "hot_repeat_secs": timed["hot_repeat_secs"],
        "hot_repeat": timed["hot_repeat"],
        "hot_warmup": timed["hot_warmup"],
        "claim_boundary": _claim_boundary(),
    }


def _run_exact_prepared_row(*, county_cdb: Path, repeat: int, warmup: int) -> dict[str, object]:
    from examples.current.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (
        run_rayjoin_prepared_optix_workload,
    )

    payload = run_rayjoin_prepared_optix_workload(
        "pip",
        dataset=str(county_cdb),
        result_mode="count",
        count_mode="exact",
        query_repeat=repeat,
        warmup=warmup,
    )
    phases = payload["phases_sec"]
    return {
        "backend": "optix",
        "execution_route": "prepared_optix_exact_count",
        "dataset": str(county_cdb),
        "row_count": int(payload["row_count"]),
        "hot_median_sec": float(phases["prepared_query_sec"]),
        "hot_total_sec": float(phases["prepared_query_sec_total_sec"]),
        "hot_repeat": int(phases["prepared_query_sec_repeat"]),
        "hot_warmup": int(phases["prepared_query_sec_warmup"]),
        "claim_boundary": payload.get("claim_boundary", _claim_boundary()),
    }


def run_timing(args: argparse.Namespace) -> dict[str, object]:
    counts = _parse_counts(args.counts)
    rows = []
    for count in counts:
        county_cdb = _materialize_slice(
            args.source_cdb,
            args.data_dir / f"br_county_start{args.start}_count{count}.cdb",
            start=args.start,
            count=count,
        )
        print(f"[goal3604] count={count} CuPy dense baseline start", flush=True)
        cupy = run_cupy_baseline("pip", str(county_cdb), repeat=args.repeat, warmup=args.warmup)
        print(f"[goal3604] count={count} exact prepared OptiX start", flush=True)
        exact = _run_exact_prepared_row(county_cdb=county_cdb, repeat=args.repeat, warmup=args.warmup)
        print(f"[goal3604] count={count} boundary-event signal route start", flush=True)
        signal = _run_boundary_event_signal_row(
            county_cdb=county_cdb,
            repeat=args.repeat,
            warmup=args.warmup,
            crossing_tolerance=args.crossing_tolerance,
        )
        if int(cupy["row_count"]) != int(exact["row_count"]):
            raise RuntimeError(f"CuPy/exact count mismatch for count={count}: {cupy['row_count']} vs {exact['row_count']}")
        if not signal["counts_match_exact"]:
            raise RuntimeError(f"boundary-event signal count mismatch for count={count}")
        rows.append(
            {
                "chain_count": count,
                "county_cdb": str(county_cdb),
                "cupy_dense_cuda_core": cupy,
                "prepared_optix_exact": exact,
                "boundary_event_signal_route": signal,
                "exact_counts_match": True,
                "prepared_optix_exact_speedup_vs_cupy": float(cupy["hot_median_sec"]) / float(exact["hot_median_sec"]),
                "boundary_event_signal_speedup_vs_cupy": float(cupy["hot_median_sec"]) / float(signal["hot_median_sec"]),
                "boundary_event_signal_speedup_vs_prepared_exact": float(exact["hot_median_sec"])
                / float(signal["hot_median_sec"]),
                "claim_boundary": _claim_boundary(),
            }
        )
    signal_ratios = [float(row["boundary_event_signal_speedup_vs_cupy"]) for row in rows]
    exact_ratios = [float(row["prepared_optix_exact_speedup_vs_cupy"]) for row in rows]
    return {
        "schema": SCHEMA,
        "goal": 3604,
        "generated_at_unix": time.time(),
        "git_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "git_status_short": _command_output(["git", "status", "--short"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "source_cdb": str(args.source_cdb),
        "data_dir": str(args.data_dir),
        "start": int(args.start),
        "counts": list(counts),
        "repeat": int(args.repeat),
        "warmup": int(args.warmup),
        "crossing_tolerance": float(args.crossing_tolerance),
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "all_counts_match": all(bool(row["exact_counts_match"]) for row in rows),
            "all_boundary_event_signal_counts_match_exact": all(
                bool(row["boundary_event_signal_route"]["counts_match_exact"]) for row in rows
            ),
            "geomean_prepared_optix_exact_speedup_vs_cupy": (
                math.prod(exact_ratios) ** (1.0 / len(exact_ratios)) if exact_ratios else None
            ),
            "geomean_boundary_event_signal_speedup_vs_cupy": (
                math.prod(signal_ratios) ** (1.0 / len(signal_ratios)) if signal_ratios else None
            ),
            "min_boundary_event_signal_speedup_vs_cupy": min(signal_ratios) if signal_ratios else None,
        },
        "interpretation": (
            "Internal timing scout for the generic boundary-event selective PIP route. "
            "The route remains app-agnostic at the engine level and compares against the "
            "current dense CuPy scalar-count baseline and exact prepared OptiX count. "
            "This packet does not authorize public RayJoin, RT-core, or speedup claims."
        ),
        "claim_boundary": _claim_boundary(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3604 RayJoin PIP boundary-event signal timing.")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data" / "rayjoin_public_cdb")
    parser.add_argument("--source-cdb", type=Path, default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb")
    parser.add_argument("--start", type=int, default=256)
    parser.add_argument("--counts", default="512")
    parser.add_argument("--repeat", type=int, default=50)
    parser.add_argument("--warmup", type=int, default=5)
    parser.add_argument("--crossing-tolerance", type=float, default=1e-5)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.repeat <= 0:
        raise ValueError("--repeat must be positive")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")
    if args.crossing_tolerance < 0.0:
        raise ValueError("--crossing-tolerance must be non-negative")
    return args


def main() -> int:
    args = parse_args()
    payload = run_timing(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"[goal3604] wrote {args.output}", flush=True)
    print(json.dumps(payload["summary"], indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
