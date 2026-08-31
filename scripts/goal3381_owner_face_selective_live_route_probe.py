from __future__ import annotations

import argparse
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


OWNER_FACE_BY_POINT = {
    522: 248,
    523: 248,
    538: 217,
    539: 217,
    540: 212,
    564: 187,
    565: 187,
}


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
        print(f"[goal3381] downloading {source}", flush=True)
        rt.download_rayjoin_sample("br_county", source)
    if not sliced_path.exists():
        print(f"[goal3381] materializing {sliced_path}", flush=True)
        county = rt.load_cdb(source)
        sliced = CdbDataset(
            name="br_county_start256_count512",
            chains=tuple(county.chains[256 : 256 + 512]),
        )
        rt.write_cdb(sliced, sliced_path)
    return sliced_path


def _runtime_selected_metadata(county, selected_points: tuple[int, ...]) -> dict[str, object]:
    incident_rows = rt.chains_to_incident_face_candidate_rows(
        county,
        point_chain_ids=selected_points,
        endpoint_only=True,
    )
    incident_point_ids: list[int] = []
    incident_face_ids: list[int] = []
    incident_counts: list[int] = []
    rank0: list[int] = []
    for row in incident_rows:
        point_id = int(row["point_id"])
        face_id = int(row["face_id"])
        incident_point_ids.append(point_id)
        incident_face_ids.append(face_id)
        incident_counts.append(int(row["incident_face_count"]))
        rank0.append(0 if face_id == OWNER_FACE_BY_POINT[point_id] else 10 + face_id)

    priority = rt.derive_owner_face_priority_columns_from_rank_signals(
        point_ids=incident_point_ids,
        face_ids=incident_face_ids,
        rank_columns={"rank0": tuple(rank0)},
        rank_fields=("rank0",),
    )
    observed_owner_points = {
        int(row["point_id"])
        for row in incident_rows
        if int(row["face_id"]) == OWNER_FACE_BY_POINT[int(row["point_id"])]
    }
    return {
        "incident_point_ids": tuple(incident_point_ids),
        "incident_face_ids": tuple(incident_face_ids),
        "incident_counts": tuple(incident_counts),
        "priority_point_ids": priority["point_id"],
        "priority_face_ids": priority["face_id"],
        "priorities": priority["priority"],
        "owner_face_present_for_all_selected_points": observed_owner_points == set(selected_points),
    }


def _pair_set(rows: tuple[dict[str, Any], ...]) -> set[tuple[int, int]]:
    return {(int(row["point_id"]), int(row["shape_id"])) for row in rows}


def _host_pairs(cp_module, point_ids, shape_ids) -> set[tuple[int, int]]:
    return set(
        zip(
            (int(value) for value in cp_module.asnumpy(point_ids).tolist()),
            (int(value) for value in cp_module.asnumpy(shape_ids).tolist()),
        )
    )


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    county_cdb = args.county_cdb
    if county_cdb is None:
        county_cdb = _materialize_county_slice(args.data_dir, download=args.download)

    selected_points = tuple(sorted(OWNER_FACE_BY_POINT))
    county = rt.load_cdb(county_cdb)
    points = rt.chains_to_probe_points(county)
    shapes = rt.chains_to_polygons(county)
    topology_rows = rt.chains_to_topology_rows(county)
    selected_metadata = _runtime_selected_metadata(county, selected_points)

    prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
    candidate_columns = None
    try:
        exact_rows = tuple(prepared.run(points))
        exact_pairs = _pair_set(exact_rows)
        candidate_columns = prepared.candidate_device_columns(points)
        candidates = candidate_columns.as_cupy_columns()

        filtered = rt.run_selective_closed_shape_owner_face_priority_membership_pipeline_cupy(
            incident_point_ids=cp.asarray(selected_metadata["incident_point_ids"], dtype=cp.int64),
            incident_face_ids=cp.asarray(selected_metadata["incident_face_ids"], dtype=cp.int64),
            incident_face_counts=cp.asarray(selected_metadata["incident_counts"], dtype=cp.int64),
            priority_point_ids=cp.asarray(selected_metadata["priority_point_ids"], dtype=cp.int64),
            priority_face_ids=cp.asarray(selected_metadata["priority_face_ids"], dtype=cp.int64),
            priorities=cp.asarray(selected_metadata["priorities"], dtype=cp.int64),
            candidate_point_ids=candidates["point_id"],
            candidate_shape_ids=candidates["shape_id"],
            topology_shape_ids=cp.asarray([int(row["chain_id"]) for row in topology_rows], dtype=cp.int64),
            topology_left_face_ids=cp.asarray([int(row["left_face_id"]) for row in topology_rows], dtype=cp.int64),
            topology_right_face_ids=cp.asarray([int(row["right_face_id"]) for row in topology_rows], dtype=cp.int64),
            topology_has_left_faces=cp.asarray([int(row["has_left_face"]) for row in topology_rows], dtype=cp.int8),
            topology_has_right_faces=cp.asarray([int(row["has_right_face"]) for row in topology_rows], dtype=cp.int8),
            selected_point_ids=cp.asarray(selected_points, dtype=cp.int64),
        )
        filtered_pairs = _host_pairs(cp, filtered["point_id"], filtered["shape_id"])
        candidate_pairs = _host_pairs(cp, candidates["point_id"], candidates["shape_id"])
        selected_output_pairs = {
            pair for pair in filtered_pairs if pair[0] in OWNER_FACE_BY_POINT
        }
        selected_exact_pairs = {pair for pair in exact_pairs if pair[0] in OWNER_FACE_BY_POINT}
        missing = sorted(exact_pairs - filtered_pairs)
        extra = sorted(filtered_pairs - exact_pairs)
        removed_candidate_extras = sorted(candidate_pairs - filtered_pairs)

        return {
            "schema": "rtdl.goal3381.owner_face_selective_live_route_probe.v1",
            "goal": 3381,
            "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
            "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
            "cupy_version": cp.__version__,
            "county_cdb": str(county_cdb),
            "selected_point_ids": list(selected_points),
            "selected_point_source": "caller_supplied_goal3328_known_mismatch_points",
            "selected_owner_face_source": "caller_supplied_fixture_policy_for_known_mismatch_points",
            "candidate_rows_from_optix_device_columns": True,
            "stored_candidate_artifact_used_as_input": False,
            "stored_topology_artifact_used_as_input": False,
            "stored_incident_artifact_used_as_input": False,
            "stored_exact_oracle_artifact_used_as_input": False,
            "exact_oracle_generated_by_live_optix_run": True,
            "topology_rows_derived_from_cdb": True,
            "incident_rows_derived_from_cdb": True,
            "cdb_chain_count": len(county.chains),
            "point_count": len(points),
            "shape_count": len(shapes),
            "topology_row_count": len(topology_rows),
            "incident_row_count": len(selected_metadata["incident_point_ids"]),
            "optix_candidate_row_count": int(candidate_columns.row_count),
            "optix_candidate_capacity": int(candidate_columns.capacity),
            "optix_candidate_overflow": bool(candidate_columns.overflow),
            "optix_candidate_device_resident": bool(candidate_columns.device_resident),
            "optix_candidate_traversal_seconds": float(candidate_columns.traversal_seconds),
            "exact_row_count": len(exact_pairs),
            "filtered_row_count": len(filtered_pairs),
            "candidate_extra_row_count_before_filter": len(candidate_pairs - exact_pairs),
            "removed_candidate_extra_row_count": len(removed_candidate_extras),
            "selected_candidate_row_count": int(filtered["selected_candidate_row_count"]),
            "passthrough_candidate_row_count": int(filtered["passthrough_candidate_row_count"]),
            "selected_filtered_row_count": len(selected_output_pairs),
            "selected_exact_row_count": len(selected_exact_pairs),
            "selected_output_matches_exact": selected_output_pairs == selected_exact_pairs,
            "owner_face_present_for_all_selected_points": bool(
                selected_metadata["owner_face_present_for_all_selected_points"]
            ),
            "selected_owner_face_by_point": dict(
                zip(
                    (str(int(value)) for value in cp.asnumpy(filtered["selection_point_id"]).tolist()),
                    (int(value) for value in cp.asnumpy(filtered["selection_owner_face_id"]).tolist()),
                )
            ),
            "expected_owner_face_by_point": {
                str(point_id): face_id for point_id, face_id in sorted(OWNER_FACE_BY_POINT.items())
            },
            "selected_owner_faces_match_expected": dict(
                zip(
                    (str(int(value)) for value in cp.asnumpy(filtered["selection_point_id"]).tolist()),
                    (int(value) for value in cp.asnumpy(filtered["selection_owner_face_id"]).tolist()),
                )
            )
            == {str(point_id): face_id for point_id, face_id in sorted(OWNER_FACE_BY_POINT.items())},
            "matches_exact": filtered_pairs == exact_pairs,
            "missing_exact_row_count": len(missing),
            "extra_row_count": len(extra),
            "missing_sample": [list(pair) for pair in missing[:20]],
            "extra_sample": [list(pair) for pair in extra[:20]],
            "removed_candidate_extra_sample": [list(pair) for pair in removed_candidate_extras[:20]],
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
                "Selective live route probe: OptiX produces generic candidate device columns for the full CDB "
                "slice, and the app-provided ambiguity set sends only known ambiguous point ids through the CuPy "
                "owner-face continuation while all other candidate rows pass through. This validates the "
                "selective continuation contract, but it does not discover the ambiguity set, authorize a native "
                "default route, prove zero-copy, or reproduce the RayJoin paper."
            ),
        }
    finally:
        if candidate_columns is not None:
            candidate_columns.close()
        prepared.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3381 selective owner-face live-route probe.")
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
