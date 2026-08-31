from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402
from rtdsl.datasets import CdbDataset  # noqa: E402


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _materialize_slice(source: Path, output: Path, *, start: int, count: int) -> Path:
    if output.exists():
        return output
    source_dataset = rt.load_cdb(source)
    sliced = CdbDataset(
        name=f"{source.stem}_start{start}_count{count}",
        chains=tuple(source_dataset.chains[start : start + count]),
    )
    rt.write_cdb(sliced, output)
    return output


def _pair_set(rows: tuple[dict[str, Any], ...]) -> set[tuple[int, int]]:
    return {(int(row["point_id"]), int(row["shape_id"])) for row in rows}


def _host_pairs(cp_module, point_ids, shape_ids) -> set[tuple[int, int]]:
    return set(
        zip(
            (int(value) for value in cp_module.asnumpy(point_ids).tolist()),
            (int(value) for value in cp_module.asnumpy(shape_ids).tolist()),
        )
    )


def _derive_selected_points_from_strict_zero_counts(
    *,
    candidate_pairs: set[tuple[int, int]],
    strict_zero_boundary_pairs: set[tuple[int, int]],
) -> tuple[int, ...]:
    candidate_by_point: dict[int, set[int]] = defaultdict(set)
    zero_by_point: dict[int, set[int]] = defaultdict(set)
    for point_id, shape_id in candidate_pairs:
        candidate_by_point[point_id].add(shape_id)
    for point_id, shape_id in strict_zero_boundary_pairs:
        if (point_id, shape_id) in candidate_pairs:
            zero_by_point[point_id].add(shape_id)
    selected = []
    for point_id in sorted(candidate_by_point):
        candidate_count = len(candidate_by_point[point_id])
        zero_count = len(zero_by_point[point_id])
        if candidate_count > zero_count and zero_count <= 2:
            selected.append(point_id)
    return tuple(selected)


def _run_one(
    *,
    county_cdb: Path,
    crossing_tolerance: float,
) -> dict[str, object]:
    import cupy as cp  # type: ignore
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    county = rt.load_cdb(county_cdb)
    points = rt.chains_to_probe_points(county)
    shapes = rt.chains_to_polygons(county)
    prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
    candidate_columns = None
    boundary_columns = None
    try:
        exact_pairs = _pair_set(tuple(prepared.run(points)))
        candidate_columns = prepared.candidate_device_columns(points)
        candidate_cupy = candidate_columns.as_cupy_columns()
        candidate_pairs = _host_pairs(cp, candidate_cupy["point_id"], candidate_cupy["shape_id"])
        boundary_columns = prepared.first_boundary_crossing_device_columns(
            points,
            max_rows=len(points) * len(shapes),
        )
        boundary_cupy = boundary_columns.as_cupy_columns()
        strict_zero_mask = cp.abs(boundary_cupy["crossing_t"]) == 0.0
        strict_zero_boundary_pairs = _host_pairs(
            cp,
            boundary_cupy["point_id"][strict_zero_mask],
            boundary_cupy["shape_id"][strict_zero_mask],
        )
        selected_points = _derive_selected_points_from_strict_zero_counts(
            candidate_pairs=candidate_pairs,
            strict_zero_boundary_pairs=strict_zero_boundary_pairs,
        )
        filtered = rt.run_selective_closed_shape_boundary_event_membership_pipeline_cupy(
            candidate_point_ids=candidate_cupy["point_id"],
            candidate_shape_ids=candidate_cupy["shape_id"],
            boundary_point_ids=boundary_cupy["point_id"],
            boundary_shape_ids=boundary_cupy["shape_id"],
            boundary_crossing_t=boundary_cupy["crossing_t"],
            selected_point_ids=cp.asarray(selected_points, dtype=cp.int64),
            crossing_tolerance=crossing_tolerance,
        )
        filtered_pairs = _host_pairs(cp, filtered["point_id"], filtered["shape_id"])
    finally:
        if boundary_columns is not None:
            boundary_columns.close()
        if candidate_columns is not None:
            candidate_columns.close()
        prepared.close()

    true_extra_points = sorted({point_id for point_id, shape_id in candidate_pairs - exact_pairs})
    selected_set = set(selected_points)
    missing = sorted(exact_pairs - filtered_pairs)
    extra = sorted(filtered_pairs - exact_pairs)
    return {
        "county_cdb": str(county_cdb),
        "point_count": len(points),
        "shape_count": len(shapes),
        "optix_candidate_row_count": int(candidate_columns.row_count),
        "boundary_event_row_count": int(boundary_columns.row_count),
        "boundary_event_candidate_event_count": int(boundary_columns.candidate_event_count),
        "boundary_event_overflow": bool(boundary_columns.overflow),
        "boundary_event_device_resident": bool(boundary_columns.device_resident),
        "exact_row_count": len(exact_pairs),
        "filtered_row_count": len(filtered_pairs),
        "candidate_extra_row_count_before_filter": len(candidate_pairs - exact_pairs),
        "selected_point_count": len(selected_points),
        "selected_point_ids": list(selected_points),
        "true_extra_point_count": len(true_extra_points),
        "true_extra_point_ids": true_extra_points,
        "selected_false_positive_point_ids": sorted(selected_set - set(true_extra_points)),
        "selected_missed_extra_point_ids": sorted(set(true_extra_points) - selected_set),
        "selected_candidate_row_count": int(filtered["selected_candidate_row_count"]),
        "selected_kept_row_count": int(filtered["selected_kept_row_count"]),
        "selected_dropped_row_count": int(filtered["selected_dropped_row_count"]),
        "passthrough_candidate_row_count": int(filtered["passthrough_candidate_row_count"]),
        "matches_exact": filtered_pairs == exact_pairs,
        "missing_exact_row_count": len(missing),
        "extra_row_count": len(extra),
        "missing_sample": [list(pair) for pair in missing[:20]],
        "extra_sample": [list(pair) for pair in extra[:20]],
    }


def run_sweep(args: argparse.Namespace) -> dict[str, object]:
    source = args.source_cdb
    counts = tuple(int(item) for item in args.counts.split(",") if item.strip())
    rows = []
    for count in counts:
        slice_path = args.data_dir / f"br_county_start{args.start}_count{count}.cdb"
        print(f"[goal3388] materialize count={count}", flush=True)
        _materialize_slice(source, slice_path, start=args.start, count=count)
        print(f"[goal3388] run count={count}", flush=True)
        rows.append(_run_one(county_cdb=slice_path, crossing_tolerance=args.crossing_tolerance))
    return {
        "schema": "rtdl.goal3388.boundary_event_tolerance_signal_slice_sweep.v1",
        "goal": 3388,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "source_cdb": str(source),
        "start": args.start,
        "counts": list(counts),
        "crossing_tolerance": float(args.crossing_tolerance),
        "selected_point_signal": "candidate_count_gt_strict_zero_boundary_candidate_count_and_strict_zero_count_lte_2",
        "filter": "selected_candidate_pair_has_boundary_crossing_t_within_tolerance",
        "candidate_rows_from_optix_device_columns": True,
        "boundary_rows_from_optix_device_columns": True,
        "exact_oracle_generated_by_live_optix_run": True,
        "exact_oracle_used_only_for_signal_evaluation": True,
        "signal_inputs_exclude_exact_oracle": True,
        "rows": rows,
        "all_rows_match_exact": all(bool(row["matches_exact"]) for row in rows),
        "all_boundary_outputs_device_resident": all(bool(row["boundary_event_device_resident"]) for row in rows),
        "any_boundary_overflow": any(bool(row["boundary_event_overflow"]) for row in rows),
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rayjoin_paper_reproduction_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
            "native_default_route_authorized": False,
        },
        "interpretation": (
            "Bounded multi-slice sweep: strict-zero boundary-event count selects likely ambiguous points, "
            "and a small explicit crossing tolerance keeps legitimate near-zero rows while the generic "
            "boundary-event CuPy filter removes candidate extras. This is not a default route; it is a "
            "scale characterization of a candidate signal over county slices."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3388 boundary-event tolerance signal slice sweep.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb",
    )
    parser.add_argument(
        "--source-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb",
    )
    parser.add_argument("--start", type=int, default=256)
    parser.add_argument("--counts", default="512,1024,2048")
    parser.add_argument("--crossing-tolerance", type=float, default=1e-5)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_sweep(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
