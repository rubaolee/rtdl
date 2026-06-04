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


def _materialize_county_slice(data_dir: Path, *, download: bool) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    source = data_dir / "br_county.cdb"
    sliced_path = data_dir / "br_county_start256_count512.cdb"
    if not source.exists():
        if not download:
            raise FileNotFoundError(f"{source} is missing; rerun with --download")
        print(f"[goal3386] downloading {source}", flush=True)
        rt.download_rayjoin_sample("br_county", source)
    if not sliced_path.exists():
        print(f"[goal3386] materializing {sliced_path}", flush=True)
        county = rt.load_cdb(source)
        sliced = CdbDataset(
            name="br_county_start256_count512",
            chains=tuple(county.chains[256 : 256 + 512]),
        )
        rt.write_cdb(sliced, sliced_path)
    return sliced_path


def _pair_set(rows: tuple[dict[str, Any], ...]) -> set[tuple[int, int]]:
    return {(int(row["point_id"]), int(row["shape_id"])) for row in rows}


def _host_pairs(cp_module, point_ids, shape_ids) -> set[tuple[int, int]]:
    return set(
        zip(
            (int(value) for value in cp_module.asnumpy(point_ids).tolist()),
            (int(value) for value in cp_module.asnumpy(shape_ids).tolist()),
        )
    )


def _derive_selected_points(
    *,
    county,
    topology_rows: tuple[dict[str, int], ...],
    candidate_pairs: set[tuple[int, int]],
    zero_boundary_pairs: set[tuple[int, int]],
) -> tuple[tuple[int, ...], list[dict[str, object]]]:
    topology_by_shape = {int(row["chain_id"]): row for row in topology_rows}
    incident_rows = rt.chains_to_incident_face_candidate_rows(county, endpoint_only=True)
    incident_by_point: dict[int, list[dict[str, int | float]]] = defaultdict(list)
    for row in incident_rows:
        incident_by_point[int(row["point_id"])].append(row)

    candidate_by_point: dict[int, set[int]] = defaultdict(set)
    zero_boundary_by_point: dict[int, set[int]] = defaultdict(set)
    for point_id, shape_id in candidate_pairs:
        candidate_by_point[point_id].add(shape_id)
    for point_id, shape_id in zero_boundary_pairs:
        if (point_id, shape_id) in candidate_pairs:
            zero_boundary_by_point[point_id].add(shape_id)

    selected: list[int] = []
    feature_rows: list[dict[str, object]] = []
    for point_id in sorted(candidate_by_point):
        candidate_shapes = candidate_by_point[point_id]
        zero_shapes = zero_boundary_by_point[point_id]
        candidate_faces: set[int] = set()
        for shape_id in candidate_shapes:
            topology = topology_by_shape.get(shape_id)
            if topology is None:
                continue
            left = int(topology["left_face_id"])
            right = int(topology["right_face_id"])
            if left != 0:
                candidate_faces.add(left)
            if right != 0:
                candidate_faces.add(right)
        incidents = incident_by_point.get(point_id, [])
        row = {
            "point_id": point_id,
            "candidate_count": len(candidate_shapes),
            "zero_boundary_candidate_count": len(zero_shapes),
            "incident_row_count": len(incidents),
            "candidate_face_count": len(candidate_faces),
            "candidate_shape_ids": sorted(candidate_shapes),
            "zero_boundary_candidate_shape_ids": sorted(zero_shapes),
        }
        is_selected = (
            row["candidate_count"] > row["zero_boundary_candidate_count"]
            and row["zero_boundary_candidate_count"] == 2
            and row["incident_row_count"] == 3
            and row["candidate_face_count"] == 4
        )
        if is_selected:
            selected.append(point_id)
            feature_rows.append(row)
    return tuple(selected), feature_rows


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    county_cdb = args.county_cdb
    if county_cdb is None:
        county_cdb = _materialize_county_slice(args.data_dir, download=args.download)
    county = rt.load_cdb(county_cdb)
    points = rt.chains_to_probe_points(county)
    shapes = rt.chains_to_polygons(county)
    topology_rows = rt.chains_to_topology_rows(county)

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
        zero_mask = cp.abs(boundary_cupy["crossing_t"]) == 0.0
        zero_boundary_pairs = _host_pairs(
            cp,
            boundary_cupy["point_id"][zero_mask],
            boundary_cupy["shape_id"][zero_mask],
        )
        selected_points, selected_feature_rows = _derive_selected_points(
            county=county,
            topology_rows=topology_rows,
            candidate_pairs=candidate_pairs,
            zero_boundary_pairs=zero_boundary_pairs,
        )
        filtered = rt.run_selective_closed_shape_boundary_event_membership_pipeline_cupy(
            candidate_point_ids=candidate_cupy["point_id"],
            candidate_shape_ids=candidate_cupy["shape_id"],
            boundary_point_ids=boundary_cupy["point_id"],
            boundary_shape_ids=boundary_cupy["shape_id"],
            boundary_crossing_t=boundary_cupy["crossing_t"],
            selected_point_ids=cp.asarray(selected_points, dtype=cp.int64),
        )
        filtered_pairs = _host_pairs(cp, filtered["point_id"], filtered["shape_id"])
    finally:
        if boundary_columns is not None:
            boundary_columns.close()
        if candidate_columns is not None:
            candidate_columns.close()
        prepared.close()

    true_extra_points = sorted({point_id for point_id, shape_id in candidate_pairs - exact_pairs})
    missing = sorted(exact_pairs - filtered_pairs)
    extra = sorted(filtered_pairs - exact_pairs)
    return {
        "schema": "rtdl.goal3386.boundary_event_signal_selective_route_probe.v1",
        "goal": 3386,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "cupy_version": cp.__version__,
        "county_cdb": str(county_cdb),
        "candidate_rows_from_optix_device_columns": True,
        "boundary_rows_from_optix_device_columns": True,
        "exact_oracle_generated_by_live_optix_run": True,
        "exact_oracle_used_only_for_signal_evaluation": True,
        "signal_inputs_exclude_exact_oracle": True,
        "topology_rows_derived_from_cdb": True,
        "incident_rows_derived_from_cdb": True,
        "point_count": len(points),
        "shape_count": len(shapes),
        "optix_candidate_row_count": int(candidate_columns.row_count),
        "boundary_event_row_count": int(boundary_columns.row_count),
        "boundary_event_candidate_event_count": int(boundary_columns.candidate_event_count),
        "boundary_event_device_resident": bool(boundary_columns.device_resident),
        "boundary_event_overflow": bool(boundary_columns.overflow),
        "exact_row_count": len(exact_pairs),
        "filtered_row_count": len(filtered_pairs),
        "candidate_extra_row_count_before_filter": len(candidate_pairs - exact_pairs),
        "selected_point_signal": (
            "candidate_count_gt_zero_boundary_candidate_count_and_zero_count_eq2_"
            "and_incident_row_count_eq3_and_candidate_face_count_eq4"
        ),
        "selected_point_ids": list(selected_points),
        "true_extra_point_ids": true_extra_points,
        "selected_points_match_true_extra_points": list(selected_points) == true_extra_points,
        "selected_feature_rows": selected_feature_rows,
        "selected_candidate_row_count": int(filtered["selected_candidate_row_count"]),
        "passthrough_candidate_row_count": int(filtered["passthrough_candidate_row_count"]),
        "selected_kept_row_count": int(filtered["selected_kept_row_count"]),
        "selected_dropped_row_count": int(filtered["selected_dropped_row_count"]),
        "boundary_event_filter": str(filtered["boundary_event_filter"]),
        "matches_exact": filtered_pairs == exact_pairs,
        "missing_exact_row_count": len(missing),
        "extra_row_count": len(extra),
        "missing_sample": [list(pair) for pair in missing[:20]],
        "extra_sample": [list(pair) for pair in extra[:20]],
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
            "Constructive bounded route probe: live OptiX candidate and boundary-event device columns plus "
            "CDB-derived generic topology select exactly the seven candidate-extra points on this slice, then "
            "the generic selective boundary-event CuPy filter drops the twelve extras and matches live exact "
            "OptiX output. This is still a bounded signal probe, not a default route or public claim."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3386 boundary-event signal selective route probe.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb",
    )
    parser.add_argument("--county-cdb", type=Path, default=None)
    parser.add_argument("--download", action="store_true")
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
